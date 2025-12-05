"""
Tests for parse_document_async tool
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from tools.parse_document_async import ParseDocumentAsyncTool


class TestParseDocumentAsyncTool:
    """Test cases for ParseDocumentAsyncTool"""

    def test_successful_task_submission(self, mock_runtime, mock_session, mock_file, mock_successful_submit_response):
        """Test successful document submission"""
        tool = ParseDocumentAsyncTool(runtime=mock_runtime, session=mock_session)

        tool_parameters = {
            'file': mock_file,
            'backend': 'pipeline',
            'lang': 'ch',
            'formula_enable': True,
            'table_enable': True,
            'priority': 5
        }

        with patch('tools.parse_document_async.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = mock_successful_submit_response
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            messages = list(tool._invoke(tool_parameters))

            # Should return 3 messages: text (task_id), json, and 2 variables
            assert len(messages) >= 3

            # First message should be the pure task_id
            text_messages = [msg for msg in messages if hasattr(msg, 'message') and isinstance(msg.message, str)]
            assert any('test-task-id-12345' in msg.message for msg in text_messages)

    def test_missing_api_server_url(self, mock_file):
        """Test error when API server URL is not configured"""
        tool = ParseDocumentAsyncTool()
        tool.runtime = Mock()
        tool.runtime.credentials = {}

        tool_parameters = {
            'file': mock_file
        }

        messages = list(tool._invoke(tool_parameters))

        # Should return error message
        assert len(messages) > 0
        assert any('API Server URL is not configured' in str(msg) for msg in messages)

    def test_missing_file(self, mock_runtime):
        """Test error when no file is provided"""
        tool = ParseDocumentAsyncTool()
        tool.runtime = mock_runtime

        tool_parameters = {}

        messages = list(tool._invoke(tool_parameters))

        # Should return error message
        assert len(messages) > 0
        assert any('No file provided' in str(msg) for msg in messages)

    def test_api_returns_success_but_no_task_id(self, mock_runtime, mock_file):
        """Test error when API returns success but no task_id"""
        tool = ParseDocumentAsyncTool()
        tool.runtime = mock_runtime

        tool_parameters = {
            'file': mock_file
        }

        with patch('tools.parse_document_async.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                'success': True
                # No task_id
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            messages = list(tool._invoke(tool_parameters))

            # Should return error message about missing task_id
            assert any('no task_id' in str(msg).lower() for msg in messages)

    def test_api_returns_failure(self, mock_runtime, mock_file):
        """Test error when API returns failure"""
        tool = ParseDocumentAsyncTool()
        tool.runtime = mock_runtime

        tool_parameters = {
            'file': mock_file
        }

        with patch('tools.parse_document_async.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                'success': False,
                'message': 'Invalid file format'
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            messages = list(tool._invoke(tool_parameters))

            # Should return error message
            assert any('Failed to submit task' in str(msg) for msg in messages)
            assert any('Invalid file format' in str(msg) for msg in messages)

    def test_network_error(self, mock_runtime, mock_file):
        """Test handling of network errors"""
        tool = ParseDocumentAsyncTool()
        tool.runtime = mock_runtime

        tool_parameters = {
            'file': mock_file
        }

        with patch('tools.parse_document_async.requests.post') as mock_post:
            mock_post.side_effect = Exception("Network error: Connection refused")

            messages = list(tool._invoke(tool_parameters))

            # Should return error message
            assert any('Error' in str(msg) for msg in messages)

    def test_default_parameters(self, mock_runtime, mock_file, mock_successful_submit_response):
        """Test that default parameters are used correctly"""
        tool = ParseDocumentAsyncTool()
        tool.runtime = mock_runtime

        tool_parameters = {
            'file': mock_file
            # No other parameters - should use defaults
        }

        with patch('tools.parse_document_async.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = mock_successful_submit_response
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            messages = list(tool._invoke(tool_parameters))

            # Verify post was called with default values
            call_args = mock_post.call_args
            assert call_args is not None
            data = call_args[1]['data']
            assert data['backend'] == 'pipeline'
            assert data['lang'] == 'ch'
            assert data['priority'] == '0'
