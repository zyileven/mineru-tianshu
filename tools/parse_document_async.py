from collections.abc import Generator
from typing import Any
import requests
from io import BytesIO

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class ParseDocumentAsyncTool(Tool):
    """
    Asynchronous document parsing tool.
    Submits a document to MinerU Tianshu and returns task_id immediately.
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
        priority = tool_parameters.get('priority', 0)

        if not file:
            yield self.create_text_message("Error: No file provided")
            return

        try:
            # Get file content
            file_name = file.filename or 'document.pdf'

            # Try to get file content, handling the case where blob property might fail
            try:
                file_content = file.blob
            except ValueError as e:
                # If blob fails due to missing FILES_URL, file should already have _blob set
                if hasattr(file, '_blob') and file._blob:
                    file_content = file._blob
                else:
                    yield self.create_text_message(
                        f"❌ Error: Unable to access file content. "
                        f"This usually means the Dify server needs to configure the FILES_URL environment variable. "
                        f"Error details: {str(e)}"
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
                'priority': str(priority)
            }

            # Prepare headers with optional API key
            headers = {}
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'

            # Submit the task
            submit_url = f"{api_server_url}/api/v1/tasks/submit"
            response = requests.post(submit_url, files=files, data=data, headers=headers, timeout=60)
            response.raise_for_status()
            result = response.json()

            # Check business-level success first
            if not result.get('success'):
                error_msg = result.get('message') or result.get('error_message', 'Unknown error')
                yield self.create_text_message(f"❌ Failed to submit task: {error_msg}")
                return

            # Validate task_id existence
            task_id = result.get('task_id')
            if not task_id:
                yield self.create_text_message(f"❌ Error: API returned success but no task_id. Response: {result}")
                return

            # Return task_id as text output (primary output - pure string only)
            yield self.create_text_message(task_id)

            # Return enhanced API response as JSON with friendly message
            json_response = {
                'task_id': task_id,
                'success': result.get('success'),
                'file_name': file_name,
                'backend': backend,
                'message': (
                    f"✅ Document submitted successfully!\n"
                    f"📝 File: {file_name}\n"
                    f"🆔 Task ID: {task_id}\n"
                    f"⏳ Use the 'get_parse_result' tool to check processing status."
                ),
                'api_response': result  # Original API response
            }
            yield self.create_json_message(json_response)

            # Also create variables for easy access
            yield self.create_variable_message('task_id', task_id)
            yield self.create_variable_message('result', result)

        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"❌ Network error: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"❌ Error: {str(e)}")
