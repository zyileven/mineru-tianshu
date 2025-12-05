"""
Tests for parse_document tool (synchronous)
"""
import pytest
from unittest.mock import Mock, patch
from tools.parse_document import ParseDocumentTool


class TestParseDocumentTool:
    """Test cases for ParseDocumentTool"""

    def test_successful_sync_parse(self, mock_runtime, mock_file):
        """Test successful synchronous document parsing"""
        tool = ParseDocumentTool()
        tool.runtime = mock_runtime

        tool_parameters = {
            'file': mock_file,
            'backend': 'pipeline',
            'lang': 'ch',
            'formula_enable': True,
            'table_enable': True,
            'max_wait_time': 300
        }

        with patch('tools.parse_document.requests.post') as mock_post, \
             patch('tools.parse_document.requests.get') as mock_get:

            # Mock submit response
            mock_submit_response = Mock()
            mock_submit_response.json.return_value = {
                'success': True,
                'task_id': 'test-task-id-12345'
            }
            mock_submit_response.raise_for_status = Mock()
            mock_post.return_value = mock_submit_response

            # Mock status check response (completed immediately)
            mock_status_response = Mock()
            mock_status_response.json.return_value = {
                'success': True,
                'status': 'completed',
                'task_id': 'test-task-id-12345',
                'file_name': 'test_document.pdf',
                'backend': 'pipeline',
                'data': {
                    'content': '# Test Document\n\nThis is test content.',
                    'markdown_file': 'test_document.md'
                }
            }
            mock_status_response.raise_for_status = Mock()
            mock_get.return_value = mock_status_response

            messages = list(tool._invoke(tool_parameters))

            # Should return success messages with content
            assert len(messages) > 0
            assert any('completed' in str(msg).lower() for msg in messages)
            assert any('Test Document' in str(msg) for msg in messages)

    def test_missing_api_server_url(self, mock_file):
        """Test error when API server URL is not configured"""
        tool = ParseDocumentTool()
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
        tool = ParseDocumentTool()
        tool.runtime = mock_runtime

        tool_parameters = {}

        messages = list(tool._invoke(tool_parameters))

        # Should return error message
        assert len(messages) > 0
        assert any('No file provided' in str(msg) for msg in messages)

    def test_task_timeout(self, mock_runtime, mock_file):
        """Test timeout when task takes too long"""
        tool = ParseDocumentTool()
        tool.runtime = mock_runtime

        tool_parameters = {
            'file': mock_file,
            'max_wait_time': 1  # 1 second timeout
        }

        with patch('tools.parse_document.requests.post') as mock_post, \
             patch('tools.parse_document.requests.get') as mock_get, \
             patch('tools.parse_document.time.sleep'):

            # Mock submit response
            mock_submit_response = Mock()
            mock_submit_response.json.return_value = {
                'success': True,
                'task_id': 'test-task-id-12345'
            }
            mock_submit_response.raise_for_status = Mock()
            mock_post.return_value = mock_submit_response

            # Mock status check response (always processing)
            mock_status_response = Mock()
            mock_status_response.json.return_value = {
                'success': True,
                'status': 'processing',
                'task_id': 'test-task-id-12345'
            }
            mock_status_response.raise_for_status = Mock()
            mock_get.return_value = mock_status_response

            messages = list(tool._invoke(tool_parameters))

            # Should return timeout message
            assert any('timeout' in str(msg).lower() or 'exceeded' in str(msg).lower() for msg in messages)

    def test_task_fails_during_processing(self, mock_runtime, mock_file):
        """Test when task fails during processing"""
        tool = ParseDocumentTool()
        tool.runtime = mock_runtime

        tool_parameters = {
            'file': mock_file
        }

        with patch('tools.parse_document.requests.post') as mock_post, \
             patch('tools.parse_document.requests.get') as mock_get, \
             patch('tools.parse_document.time.sleep'):

            # Mock submit response
            mock_submit_response = Mock()
            mock_submit_response.json.return_value = {
                'success': True,
                'task_id': 'test-task-id-12345'
            }
            mock_submit_response.raise_for_status = Mock()
            mock_post.return_value = mock_submit_response

            # Mock status check response (failed)
            mock_status_response = Mock()
            mock_status_response.json.return_value = {
                'success': True,
                'status': 'failed',
                'task_id': 'test-task-id-12345',
                'error_message': 'Invalid PDF format'
            }
            mock_status_response.raise_for_status = Mock()
            mock_get.return_value = mock_status_response

            messages = list(tool._invoke(tool_parameters))

            # Should return failure message
            assert any('failed' in str(msg).lower() for msg in messages)
            assert any('Invalid PDF format' in str(msg) for msg in messages)

    def test_default_parameters(self, mock_runtime, mock_file):
        """Test that default parameters are used correctly"""
        tool = ParseDocumentTool()
        tool.runtime = mock_runtime

        tool_parameters = {
            'file': mock_file
            # No other parameters - should use defaults
        }

        with patch('tools.parse_document.requests.post') as mock_post, \
             patch('tools.parse_document.requests.get') as mock_get:

            # Mock submit response
            mock_submit_response = Mock()
            mock_submit_response.json.return_value = {
                'success': True,
                'task_id': 'test-task-id-12345'
            }
            mock_submit_response.raise_for_status = Mock()
            mock_post.return_value = mock_submit_response

            # Mock status check response
            mock_status_response = Mock()
            mock_status_response.json.return_value = {
                'success': True,
                'status': 'completed',
                'data': {'content': 'Test'}
            }
            mock_status_response.raise_for_status = Mock()
            mock_get.return_value = mock_status_response

            messages = list(tool._invoke(tool_parameters))

            # Verify post was called with default values
            call_args = mock_post.call_args
            assert call_args is not None
            data = call_args[1]['data']
            assert data['backend'] == 'pipeline'
            assert data['lang'] == 'ch'

    def test_network_error(self, mock_runtime, mock_file):
        """Test handling of network errors"""
        tool = ParseDocumentTool()
        tool.runtime = mock_runtime

        tool_parameters = {
            'file': mock_file
        }

        with patch('tools.parse_document.requests.post') as mock_post:
            mock_post.side_effect = Exception("Network error: Connection refused")

            messages = list(tool._invoke(tool_parameters))

            # Should return error message
            assert any('Error' in str(msg) for msg in messages)
