from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class GetParseResultTool(Tool):
    """
    Get parsing result for a submitted task.

    Output channels are separated by purpose:
      - text : the final parsed Markdown content (clean, complete, no status noise)
      - log  : progress / status updates (do not pollute the text output)
      - json : structured metadata (markdown_content, task_id, status, ... + originData)
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

        # Properly convert include_images to boolean (handles "true"/"1"/"yes")
        include_images_raw = tool_parameters.get('include_images', False)
        if isinstance(include_images_raw, str):
            include_images = include_images_raw.lower() in ('true', '1', 'yes')
        else:
            include_images = bool(include_images_raw)

        if not task_id:
            yield self.create_text_message("Error: task_id is required")
            return

        try:
            yield self.create_log_message("Checking task status", {"task_id": task_id})

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
                yield self.create_text_message(f"Failed to get task status: {error_msg}")
                return

            task_status = result.get('status')
            file_name = result.get('file_name')
            backend = result.get('backend')
            created_at = result.get('created_at')
            started_at = result.get('started_at')
            completed_at = result.get('completed_at')
            error_message = result.get('error_message')

            yield self.create_log_message(
                "Task status retrieved",
                {"status": task_status, "file_name": file_name, "backend": backend},
            )

            # Parent task (large document split) progress -> logs
            if result.get('is_parent'):
                subtask_progress = result.get('subtask_progress', {})
                yield self.create_log_message(
                    "Large document progress",
                    {
                        "total": subtask_progress.get('total', 0),
                        "completed": subtask_progress.get('completed', 0),
                        "percentage": subtask_progress.get('percentage', 0),
                    },
                )

            if task_status == 'completed':
                yield self.create_log_message("Task completed", {"completed_at": completed_at})

                data_field = result.get('data', {}) or {}
                markdown_content = data_field.get('content')
                markdown_file = data_field.get('markdown_file', '')

                if markdown_content:
                    # text output = the full, clean Markdown content (no truncation)
                    yield self.create_text_message(markdown_content)

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
                        'originData': result,
                    }

                    # Image download URLs from the dedicated images endpoint (RustFS)
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
                            yield self.create_log_message("Could not retrieve image list", {"error": str(img_err)})

                        if images:
                            result_json['images'] = images
                            yield self.create_log_message("Extracted images", {"count": len(images)})

                    yield self.create_json_message(result_json)
                else:
                    yield self.create_text_message(
                        "Task completed but no content found. The result files may have been cleaned up."
                    )
                    yield self.create_json_message({
                        'task_id': task_id,
                        'status': 'completed',
                        'file_name': file_name,
                        'markdown_content': '',
                        'message': 'Result files have been cleaned up (older than retention period)',
                        'originData': result,
                    })

            elif task_status == 'failed':
                yield self.create_text_message(f"Processing failed: {error_message or 'Unknown error'}")
                yield self.create_json_message({
                    'task_id': task_id,
                    'status': 'failed',
                    'file_name': file_name,
                    'error_message': error_message,
                    'originData': result,
                })

            elif task_status in ('processing', 'pending'):
                note = (
                    "Task is still being processed. Please check again later."
                    if task_status == 'processing'
                    else "Task is pending in the queue. Please check again later."
                )
                yield self.create_text_message(note)
                yield self.create_json_message({
                    'task_id': task_id,
                    'status': task_status,
                    'file_name': file_name,
                    'created_at': created_at,
                    'started_at': started_at,
                    'message': note,
                    'originData': result,
                })

            else:
                yield self.create_text_message(f"Unknown status: {task_status}")
                yield self.create_json_message({
                    'task_id': task_id,
                    'status': task_status,
                    'file_name': file_name,
                    'originData': result,
                })

        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Network error: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
