"""
Tests for get_parse_result tool
"""
import pytest
from unittest.mock import Mock, patch
from tools.get_parse_result import GetParseResultTool


class TestGetParseResultTool:
    """Test cases for GetParseResultTool"""

    def test_get_completed_task_result(self, mock_runtime, mock_completed_task_response):
        """Test retrieving completed task result"""
        tool = GetParseResultTool()
        tool.runtime = mock_runtime

        tool_parameters = {
            'task_id': 'test-task-id-12345',
            'include_images': False
        }

        with patch('tools.get_parse_result.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_completed_task_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            messages = list(tool._invoke(tool_parameters))

            # Should return status messages and content
            assert len(messages) > 0
            assert any('completed' in str(msg).lower() for msg in messages)
            assert any('Test Document' in str(msg) for msg in messages)

    def test_get_pending_task_status(self, mock_runtime, mock_pending_task_response):
        """Test retrieving pending task status"""
        tool = GetParseResultTool()
        tool.runtime = mock_runtime

        tool_parameters = {
            'task_id': 'test-task-id-12345'
        }

        with patch('tools.get_parse_result.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_pending_task_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            messages = list(tool._invoke(tool_parameters))

            # Should return pending status
            assert any('pending' in str(msg).lower() for msg in messages)

    def test_get_processing_task_status(self, mock_runtime, mock_processing_task_response):
        """Test retrieving processing task status"""
        tool = GetParseResultTool()
        tool.runtime = mock_runtime

        tool_parameters = {
            'task_id': 'test-task-id-12345'
        }

        with patch('tools.get_parse_result.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_processing_task_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            messages = list(tool._invoke(tool_parameters))

            # Should return processing status
            assert any('processing' in str(msg).lower() for msg in messages)

    def test_get_failed_task_result(self, mock_runtime, mock_failed_task_response):
        """Test retrieving failed task result"""
        tool = GetParseResultTool()
        tool.runtime = mock_runtime

        tool_parameters = {
            'task_id': 'test-task-id-12345'
        }

        with patch('tools.get_parse_result.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_failed_task_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            messages = list(tool._invoke(tool_parameters))

            # Should return failed status and error message
            assert any('failed' in str(msg).lower() for msg in messages)
            assert any('invalid format' in str(msg).lower() for msg in messages)

    def test_missing_api_server_url(self):
        """Test error when API server URL is not configured"""
        tool = GetParseResultTool()
        tool.runtime = Mock()
        tool.runtime.credentials = {}

        tool_parameters = {
            'task_id': 'test-task-id-12345'
        }

        messages = list(tool._invoke(tool_parameters))

        # Should return error message
        assert len(messages) > 0
        assert any('API Server URL is not configured' in str(msg) for msg in messages)

    def test_missing_task_id(self, mock_runtime):
        """Test error when task_id is not provided"""
        tool = GetParseResultTool()
        tool.runtime = mock_runtime

        tool_parameters = {}

        messages = list(tool._invoke(tool_parameters))

        # Should return error message
        assert len(messages) > 0
        assert any('task_id is required' in str(msg) for msg in messages)

    def test_api_returns_failure(self, mock_runtime):
        """Test error when API returns failure"""
        tool = GetParseResultTool()
        tool.runtime = mock_runtime

        tool_parameters = {
            'task_id': 'invalid-task-id'
        }

        with patch('tools.get_parse_result.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                'success': False,
                'message': 'Task not found'
            }
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            messages = list(tool._invoke(tool_parameters))

            # Should return error message
            assert any('Failed to get task status' in str(msg) for msg in messages)
            assert any('Task not found' in str(msg) for msg in messages)

    def test_network_error(self, mock_runtime):
        """Test handling of network errors"""
        tool = GetParseResultTool()
        tool.runtime = mock_runtime

        tool_parameters = {
            'task_id': 'test-task-id-12345'
        }

        with patch('tools.get_parse_result.requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error: Connection refused")

            messages = list(tool._invoke(tool_parameters))

            # Should return error message
            assert any('Error' in str(msg) for msg in messages)

    def test_include_images_parameter(self, mock_runtime, mock_completed_task_response):
        """Test include_images parameter"""
        tool = GetParseResultTool()
        tool.runtime = mock_runtime

        # Add images to response
        mock_completed_task_response['data']['has_images'] = True
        mock_completed_task_response['data']['images'] = [
            {'url': 'http://example.com/image1.png'},
            {'url': 'http://example.com/image2.png'}
        ]

        tool_parameters = {
            'task_id': 'test-task-id-12345',
            'include_images': True
        }

        with patch('tools.get_parse_result.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_completed_task_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            messages = list(tool._invoke(tool_parameters))

            # Verify include_images parameter was passed correctly
            call_args = mock_get.call_args
            assert call_args is not None
            params = call_args[1].get('params', {})
            assert params.get('upload_images') == 'true'

            # Should mention images in output
            assert any('image' in str(msg).lower() for msg in messages)

    def test_completed_task_without_content(self, mock_runtime):
        """Test completed task but content has been cleaned up"""
        tool = GetParseResultTool()
        tool.runtime = mock_runtime

        tool_parameters = {
            'task_id': 'test-task-id-12345'
        }

        with patch('tools.get_parse_result.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                'success': True,
                'status': 'completed',
                'task_id': 'test-task-id-12345',
                'file_name': 'test_document.pdf',
                'backend': 'pipeline',
                'created_at': '2024-01-01T00:00:00Z',
                'completed_at': '2024-01-01T00:01:00Z',
                'data': {}  # No content
            }
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            messages = list(tool._invoke(tool_parameters))

            # Should warn about missing content
            assert any('no content found' in str(msg).lower() for msg in messages)
