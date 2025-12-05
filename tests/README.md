# Testing Guide

## Current Status

✅ Test framework has been set up with:
- pytest configuration
- Test fixtures and mocks
- Test cases for all three tools

⚠️ Note: The test suite is a work in progress. Some tests may need adjustment to work with the Dify plugin framework.

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test File

```bash
pytest tests/test_parse_document_async.py
```

### Run With Coverage

```bash
pytest tests/ --cov=tools --cov-report=html
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                      # Shared fixtures and configuration
├── test_parse_document.py           # Sync tool tests
├── test_parse_document_async.py     # Async tool tests
└── test_parse_result.py             # Result retrieval tests
```

## Contributing Tests

When adding new features, please add corresponding tests. See existing test files for examples.

## Future Improvements

- [ ] Integration tests with real API
- [ ] Performance benchmarks
- [ ] End-to-end workflow tests
