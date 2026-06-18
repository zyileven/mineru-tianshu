from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class GetParseResultTool(Tool):
    """
    Get parsing result for a submitted task.
    Retrieves the status and result of a document parsing task.
    """

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Get API server URL from credentials
        api_server_url = (self.runtime.credentials.get('api_server_url') or '').rstrip('/')
        if not api_server_url:
            yield self.create_text_message("Error: API Server URL is not configured")
            return

        # Get optional API key from credentials
        api_key = self.runtime.credentials.get('api_key', '')

        # Get SSL verification setting
        verify_ssl = self.runtime.credentials.get('verify_ssl', True)

        # Get parameters
        task_id = tool_parameters.get('task_id')

        # Properly convert include_images to boolean
        # Handle string values like "true", "false", "1", "0"
        include_images_raw = tool_parameters.get('include_images', False)
        if isinstance(include_images_raw, str):
            include_images = include_images_raw.lower() in ('true', '1', 'yes')
        else:
            include_images = bool(include_images_raw)

        if not task_id:
            yield self.create_text_message("Error: task_id is required")
            return

        try:
            yield self.create_text_message(f"🔍 Checking task status: {task_id}")

            # Prepare headers with optional API key
            headers = {}
            if api_key:
                headers['X-API-Key'] = api_key

            # Query task status and result.
            # Note: extracted images are now auto-uploaded to object storage (RustFS)
            # by the server, so the deprecated `upload_images` query param is no longer
            # sent. Image download URLs are fetched from the dedicated images endpoint.
            status_url = f"{api_server_url}/api/v1/tasks/{task_id}"

            response = requests.get(status_url, headers=headers, timeout=30, verify=verify_ssl)
            response.raise_for_status()
            result = response.json()

            if not result.get('success'):
                error_msg = result.get('message', 'Unknown error')
                yield self.create_text_message(f"❌ Failed to get task status: {error_msg}")
                return

            task_status = result.get('status')
            file_name = result.get('file_name')
            backend = result.get('backend')
            created_at = result.get('created_at')
            started_at = result.get('started_at')
            completed_at = result.get('completed_at')
            error_message = result.get('error_message')

            # Display status
            yield self.create_text_message(f"📋 **Task Status:** {task_status}")

            # Display parent task progress if applicable
            if result.get('is_parent'):
                subtask_progress = result.get('subtask_progress', {})
                total = subtask_progress.get('total', 0)
                completed = subtask_progress.get('completed', 0)
                percentage = subtask_progress.get('percentage', 0)

                yield self.create_text_message(
                    f"📦 **Large Document:** {total} parts\n"
                    f"⏳ **Progress:** {completed}/{total} ({percentage:.1f}%)"
                )

                # Show subtask details
                subtasks = result.get('subtasks', [])
                if subtasks:
                    status_counts = {}
                    for st in subtasks:
                        status = st.get('status', 'unknown')
                        status_counts[status] = status_counts.get(status, 0) + 1

                    yield self.create_text_message(
                        f"📊 **Parts Status:** "
                        f"Pending: {status_counts.get('pending', 0)} | "
                        f"Processing: {status_counts.get('processing', 0)} | "
                        f"Completed: {status_counts.get('completed', 0)} | "
                        f"Failed: {status_counts.get('failed', 0)}"
                    )

            yield self.create_text_message(f"📄 **File:** {file_name}")
            yield self.create_text_message(f"⚙️ **Backend:** {backend}")

            if task_status == 'completed':
                yield self.create_text_message(f"✅ **Completed at:** {completed_at}")

                # Get the markdown content
                data_field = result.get('data', {})
                if data_field and 'content' in data_field:
                    markdown_content = data_field['content']
                    markdown_file = data_field.get('markdown_file', '')

                    # Truncate if content is too large (> 5000 characters)
                    max_preview_length = 5000
                    if len(markdown_content) > max_preview_length:
                        truncated_content = markdown_content[:max_preview_length]
                        yield self.create_text_message(
                            f"\n📄 **Parsed Document (Preview - {max_preview_length} characters)** ({markdown_file}):\n\n"
                            f"{truncated_content}\n\n"
                            f"... _(Content truncated. Total length: {len(markdown_content)} characters. "
                            f"Full content is available in the JSON response below.)_"
                        )
                    else:
                        yield self.create_text_message(f"\n📄 **Parsed Document** ({markdown_file}):\n\n{markdown_content}")

                    # Return structured result
                    result_json = {
                        'task_id': task_id,
                        'status': 'completed',
                        'file_name': file_name,
                        'backend': backend,
                        'markdown_content': markdown_content,
                        'markdown_file': markdown_file,
                        'created_at': created_at,
                        'started_at': started_at,
                        'completed_at': completed_at,
                        'originData': result  # API 原始数据
                    }

                    # Include images info if requested.
                    # Images are auto-uploaded to object storage (RustFS); their
                    # download URLs are served by the dedicated images endpoint.
                    if include_images and data_field.get('has_images', False):
                        result_json['has_images'] = True
                        images = []
                        try:
                            images_url = f"{api_server_url}/api/v1/tasks/{task_id}/images"
                            img_resp = requests.get(images_url, headers=headers, timeout=30, verify=verify_ssl)
                            img_resp.raise_for_status()
                            for img in img_resp.json().get('images', []):
                                download_url = img.get('download_url', '')
                                # Resolve relative paths against the API server base URL
                                if download_url.startswith('/'):
                                    download_url = f"{api_server_url}{download_url}"
                                images.append({**img, 'download_url': download_url})
                        except requests.exceptions.RequestException as img_err:
                            yield self.create_text_message(f"⚠️ Could not retrieve image list: {img_err}")

                        if images:
                            result_json['images'] = images
                            yield self.create_text_message(f"🖼️ This document contains {len(images)} extracted image(s)")
                        else:
                            yield self.create_text_message("🖼️ This document contains extracted images")

                    yield self.create_json_message(result_json)

                else:
                    yield self.create_text_message("⚠️ Task completed but no content found. The result files may have been cleaned up.")
                    yield self.create_json_message({
                        'task_id': task_id,
                        'status': 'completed',
                        'file_name': file_name,
                        'message': 'Result files have been cleaned up (older than retention period)',
                        'originData': result  # API 原始数据
                    })

            elif task_status == 'failed':
                yield self.create_text_message(f"❌ **Failed:** {error_message or 'Unknown error'}")
                yield self.create_json_message({
                    'task_id': task_id,
                    'status': 'failed',
                    'file_name': file_name,
                    'error_message': error_message,
                    'originData': result  # API 原始数据
                })

            elif task_status == 'processing':
                yield self.create_text_message(f"⏳ Task is still processing...")
                yield self.create_text_message(f"🕐 **Started at:** {started_at}")
                yield self.create_json_message({
                    'task_id': task_id,
                    'status': 'processing',
                    'file_name': file_name,
                    'started_at': started_at,
                    'message': 'Task is still being processed. Please check again later.',
                    'originData': result  # API 原始数据
                })

            elif task_status == 'pending':
                yield self.create_text_message(f"⏸️ Task is pending in the queue...")
                yield self.create_text_message(f"🕐 **Created at:** {created_at}")
                yield self.create_json_message({
                    'task_id': task_id,
                    'status': 'pending',
                    'file_name': file_name,
                    'created_at': created_at,
                    'message': 'Task is pending in the queue. Please check again later.',
                    'originData': result  # API 原始数据
                })

            else:
                yield self.create_text_message(f"⚠️ Unknown status: {task_status}")
                yield self.create_json_message({
                    'task_id': task_id,
                    'status': task_status,
                    'file_name': file_name,
                    'originData': result  # API 原始数据
                })

        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"❌ Network error: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"❌ Error: {str(e)}")
