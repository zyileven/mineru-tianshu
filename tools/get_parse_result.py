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
                headers['Authorization'] = f'Bearer {api_key}'

            # Query task status and result
            status_url = f"{api_server_url}/api/v1/tasks/{task_id}"
            params = {}
            if include_images:
                # Request image information to be included in the response
                params['upload_images'] = 'true'

            response = requests.get(status_url, params=params, headers=headers, timeout=30)
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

                    # Include images info if requested
                    if include_images:
                        has_images = data_field.get('has_images', False)
                        if has_images:
                            result_json['has_images'] = True
                            # Include image URLs if available
                            images = data_field.get('images', [])
                            if images:
                                result_json['images'] = images
                                yield self.create_text_message(f"🖼️ This document contains {len(images)} extracted image(s)")
                            else:
                                yield self.create_text_message(f"🖼️ This document contains extracted images")

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
