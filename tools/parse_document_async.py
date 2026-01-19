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

        # Get SSL verification setting
        verify_ssl = self.runtime.credentials.get('verify_ssl', True)

        # Get parameters
        file = tool_parameters.get('file')
        backend = tool_parameters.get('backend', 'auto')
        lang = tool_parameters.get('lang', 'auto')
        method = tool_parameters.get('method', 'auto')
        formula_enable = tool_parameters.get('formula_enable', True)
        table_enable = tool_parameters.get('table_enable', True)
        priority = tool_parameters.get('priority', 0)

        if not file:
            yield self.create_text_message("Error: No file provided")
            return

        try:
            # Get file content
            file_name = file.filename
            if not file_name:
                yield self.create_text_message("❌ Error: File object exists but filename is missing")
                return

            # Try to get file content using URL-based download to control SSL verification
            file_content = None

            # Check if file has a URL we can download from
            if hasattr(file, 'url') and file.url:
                try:
                    download_response = requests.get(
                        file.url,
                        timeout=60,
                        verify=verify_ssl
                    )
                    download_response.raise_for_status()
                    file_content = download_response.content
                except Exception as download_error:
                    # Silently try fallback method
                    pass

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
                'method': method,
                'formula_enable': str(formula_enable).lower(),
                'table_enable': str(table_enable).lower(),
                'priority': str(priority)
            }

            # Add video-specific parameters if backend is video
            if backend == 'video':
                enable_keyframe_ocr = tool_parameters.get('enable_keyframe_ocr', False)
                keep_audio = tool_parameters.get('keep_audio', False)
                ocr_backend = tool_parameters.get('ocr_backend', 'paddleocr-vl')
                keep_keyframes = tool_parameters.get('keep_keyframes', False)
                data.update({
                    'enable_keyframe_ocr': str(enable_keyframe_ocr).lower(),
                    'keep_audio': str(keep_audio).lower(),
                    'ocr_backend': ocr_backend,
                    'keep_keyframes': str(keep_keyframes).lower(),
                })

            # Add audio-specific parameters if backend is sensevoice
            if backend == 'sensevoice':
                enable_speaker_diarization = tool_parameters.get('enable_speaker_diarization', False)
                data['enable_speaker_diarization'] = str(enable_speaker_diarization).lower()

            # Add watermark removal parameters
            remove_watermark = tool_parameters.get('remove_watermark', False)
            if remove_watermark:
                watermark_conf_threshold = tool_parameters.get('watermark_conf_threshold', 0.35)
                watermark_dilation = tool_parameters.get('watermark_dilation', 10)
                data.update({
                    'remove_watermark': str(remove_watermark).lower(),
                    'watermark_conf_threshold': str(watermark_conf_threshold),
                    'watermark_dilation': str(watermark_dilation),
                })

            # Add convert_office_to_pdf parameter
            convert_office_to_pdf = tool_parameters.get('convert_office_to_pdf', False)
            if convert_office_to_pdf:
                data['convert_office_to_pdf'] = str(convert_office_to_pdf).lower()

            # Prepare headers with optional API key
            headers = {}
            if api_key:
                headers['X-API-Key'] = api_key

            # Submit the task
            submit_url = f"{api_server_url}/api/v1/tasks/submit"
            response = requests.post(submit_url, files=files, data=data, headers=headers, timeout=60, verify=verify_ssl)
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
