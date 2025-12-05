"""
Pytest configuration and shared fixtures for MinerU Tianshu tests
"""
import pytest
from unittest.mock import Mock, MagicMock, patch


@pytest.fixture
def mock_runtime():
    """Mock runtime with credentials"""
    runtime = Mock()
    runtime.credentials = {
        'api_server_url': 'http://localhost:8100',
        'api_key': 'test-api-key'
    }
    return runtime


@pytest.fixture
def mock_session():
    """Mock session"""
    return Mock()


@pytest.fixture
def mock_file():
    """Mock file object"""
    file = Mock()
    file.filename = 'test_document.pdf'
    file.blob = b'mock file content'
    file._blob = b'mock file content'
    return file


@pytest.fixture
def mock_successful_submit_response():
    """Mock successful task submission response"""
    return {
        'success': True,
        'task_id': 'test-task-id-12345',
        'message': 'Task submitted successfully'
    }


@pytest.fixture
def mock_completed_task_response():
    """Mock completed task response with content"""
    return {
        'success': True,
        'status': 'completed',
        'task_id': 'test-task-id-12345',
        'file_name': 'test_document.pdf',
        'backend': 'pipeline',
        'created_at': '2024-01-01T00:00:00Z',
        'started_at': '2024-01-01T00:00:10Z',
        'completed_at': '2024-01-01T00:01:00Z',
        'data': {
            'content': '# Test Document\n\nThis is test content.',
            'markdown_file': 'test_document.md'
        }
    }


@pytest.fixture
def mock_pending_task_response():
    """Mock pending task response"""
    return {
        'success': True,
        'status': 'pending',
        'task_id': 'test-task-id-12345',
        'file_name': 'test_document.pdf',
        'backend': 'pipeline',
        'created_at': '2024-01-01T00:00:00Z'
    }


@pytest.fixture
def mock_processing_task_response():
    """Mock processing task response"""
    return {
        'success': True,
        'status': 'processing',
        'task_id': 'test-task-id-12345',
        'file_name': 'test_document.pdf',
        'backend': 'pipeline',
        'created_at': '2024-01-01T00:00:00Z',
        'started_at': '2024-01-01T00:00:10Z'
    }


@pytest.fixture
def mock_failed_task_response():
    """Mock failed task response"""
    return {
        'success': True,
        'status': 'failed',
        'task_id': 'test-task-id-12345',
        'file_name': 'test_document.pdf',
        'backend': 'pipeline',
        'created_at': '2024-01-01T00:00:00Z',
        'started_at': '2024-01-01T00:00:10Z',
        'error_message': 'Processing failed due to invalid format'
    }
