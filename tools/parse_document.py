from collections.abc import Generator
from typing import Any
import time
import requests
from io import BytesIO
import urllib3

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ParseDocumentTool(Tool):
    """
    Synchronous document parsing tool.
    Submits a document to MinerU Tianshu and waits for processing to complete.
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
        file = tool_parameters.get('file')
        backend = tool_parameters.get('backend', 'pipeline')
        lang = tool_parameters.get('lang', 'ch')
        formula_enable = tool_parameters.get('formula_enable', True)
        table_enable = tool_parameters.get('table_enable', True)

        # Convert and validate max_wait_time
        try:
            max_wait_time = int(tool_parameters.get('max_wait_time', 300))
            if max_wait_time < 1 or max_wait_time > 3600:
                yield self.create_text_message("Error: max_wait_time must be between 1 and 3600 seconds")
                return
        except (ValueError, TypeError):
            yield self.create_text_message("Error: max_wait_time must be a valid number")
            return

        if not file:
            yield self.create_text_message("Error: No file provided")
            return

        try:
            # Step 1: Submit the task
            yield self.create_text_message(f"📤 Submitting document to MinerU Tianshu...")

            # Get file content
            file_name = file.filename or 'document.pdf'

            # Try to get file content using URL-based download to control SSL verification
            file_content = None

            # Check if file has a URL we can download from
            if hasattr(file, 'url') and file.url:
                try:
                    yield self.create_text_message(f"📥 Downloading file from URL...")
                    download_response = requests.get(
                        file.url,
                        timeout=60,
                        verify=False
                    )
                    download_response.raise_for_status()
                    file_content = download_response.content
                except Exception as download_error:
                    yield self.create_text_message(
                        f"⚠️ Failed to download from URL: {str(download_error)}"
                    )

            # Fallback: try blob property if URL download failed
            if not file_content:
                try:
                    file_content = file.blob
                except Exception as e:
                    yield self.create_text_message(
                        f"❌ Error: Unable to access file content. "
                        f"This usually means SSL certificate verification failed or FILES_URL is not configured. "
                        f"Error details: {str(e)}"
                    )
                    return

            if not file_content:
                yield self.create_text_message(
                    f"❌ Error: Could not obtain file content through any method"
                )
                return

            # Prepare form data
            files = {
                'file': (file_name, BytesIO(file_content), 'application/octet-stream')
            }
            data = {
                'backend': backend,
                'lang': lang,
                'method': 'auto',
                'formula_enable': str(formula_enable).lower(),
                'table_enable': str(table_enable).lower(),
                'priority': '0'
            }

            # Prepare headers with optional API key
            headers = {}
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'

            # Submit the task
            submit_url = f"{api_server_url}/api/v1/tasks/submit"
            response = requests.post(submit_url, files=files, data=data, headers=headers, timeout=60, verify=False)
            response.raise_for_status()
            result = response.json()

            if not result.get('success'):
                yield self.create_text_message(f"❌ Failed to submit task: {result.get('message', 'Unknown error')}")
                return

            task_id = result.get('task_id')
            if not task_id:
                yield self.create_text_message(f"❌ Error: API returned success but no task_id. Response: {result}")
                return

            yield self.create_text_message(f"✅ Task submitted successfully! Task ID: {task_id}")

            # Step 2: Poll for completion
            yield self.create_text_message(f"⏳ Waiting for processing to complete...")

            status_url = f"{api_server_url}/api/v1/tasks/{task_id}"
            start_time = time.time()
            poll_interval = 5  # Poll every 5 seconds

            while True:
                # Check timeout
                elapsed_time = time.time() - start_time
                if elapsed_time > max_wait_time:
                    yield self.create_text_message(f"⚠️ Timeout: Processing exceeded {max_wait_time} seconds. Task ID: {task_id}")
                    yield self.create_text_message("You can use the 'get_parse_result' tool to check the status later.")
                    return

                # Query task status
                status_response = requests.get(status_url, headers=headers, timeout=30, verify=False)
                status_response.raise_for_status()
                status_result = status_response.json()

                # Check API-level success first
                if not status_result.get('success'):
                    error_msg = status_result.get('message', 'Unknown error')
                    yield self.create_text_message(f"❌ API error: {error_msg}")
                    yield self.create_json_message(status_result)
                    return

                task_status = status_result.get('status')

                if task_status == 'completed':
                    # Task completed successfully
                    yield self.create_text_message(f"✅ Processing completed!")

                    # Get the markdown content with smart truncation
                    data_field = status_result.get('data', {})
                    if data_field and 'content' in data_field:
                        markdown_content = data_field['content']

                        # Truncate if content is too large (> 5000 characters)
                        max_preview_length = 5000
                        if len(markdown_content) > max_preview_length:
                            truncated_content = markdown_content[:max_preview_length]
                            yield self.create_text_message(
                                f"\n📄 **Parsed Document (Preview - {max_preview_length} characters):**\n\n"
                                f"{truncated_content}\n\n"
                                f"... _(Content truncated. Total length: {len(markdown_content)} characters. "
                                f"Full content is available in the JSON response below.)_"
                            )
                        else:
                            yield self.create_text_message(f"\n📄 **Parsed Document:**\n\n{markdown_content}")
                    else:
                        yield self.create_text_message("⚠️ Task completed but no content found. The result files may have been cleaned up.")

                    # Return API raw response directly
                    yield self.create_json_message(status_result)
                    return

                elif task_status == 'failed':
                    error_msg = status_result.get('error_message', 'Unknown error')
                    yield self.create_text_message(f"❌ Processing failed: {error_msg}")
                    # Return API raw response directly
                    yield self.create_json_message(status_result)
                    return

                elif task_status in ['pending', 'processing']:
                    # Still processing, wait and retry
                    yield self.create_text_message(f"⏳ Status: {task_status}... ({int(elapsed_time)}s elapsed)")
                    time.sleep(poll_interval)

                else:
                    # Unexpected status
                    yield self.create_text_message(f"⚠️ Unexpected status: {task_status}. Full response: {status_result.get('message', 'No additional message')}")
                    # Return API raw response directly
                    yield self.create_json_message(status_result)
                    return

        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"❌ Network error: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"❌ Error: {str(e)}")
