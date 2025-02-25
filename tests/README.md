# Time Tracker Tests

## Overview
This directory contains tests for the Time Tracker application.

## Test Structure
- `test_application_tracker.py`: Core application functionality tests
- `test_utils.py`: Utility function tests
- `test_storage.py`: Data storage and formatting tests
- `test_integration.py`: Integration tests

## Test Categories
1. Unit Tests
   - Application Tracker Tests (4 tests):
     * Initialization
     * App switching
     * Time updating
     * Final app handling
   - Utils Tests (21 tests):
     * Window information retrieval
     * Error handling
     * Edge cases
   - Storage Tests (2 tests):
     * Data grouping
     * Save functionality

2. Integration Tests (2 tests):
   - Actual window info retrieval
   - Multiple window calls

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=time_tracker

# Run specific test file
pytest tests/test_utils.py

# Run tests by marker
pytest -m "not integration"

# Run tests in parallel
pytest -n auto

# Run with detailed output
pytest -v
```

## Test Markers
- `integration`: Integration tests
- `slow`: Slow running tests
- `window`: Window handling tests
- `process`: Process handling tests
- `storage`: Storage related tests

## Best Practices
- Each test focuses on a single functionality
- Tests are independent and isolated
- Meaningful test names and docstrings
- Proper use of fixtures and mocking
- Comprehensive assertion messages

## Coverage
To generate a coverage report:
```bash
pytest --cov=time_tracker --cov-report=html
```
The report will be available in the `htmlcov` directory.


- Application Tracker: 7 tests
  ✓ Initialization
  ✓ Update app time (3 cases)
  ✓ Handle app switch
  ✓ Handle final app
  ✓ Track keyboard interrupt

- Integration Tests: 4 tests
  ✓ Actual window info
  ✓ Multiple window calls
  ✓ Full tracking cycle
  ✓ Storage integration

- Storage Tests: 4 tests
  ✓ Initialization
  ✓ Group application data
  ✓ Save data
  ✓ Display summary

- Utils Tests: 23 tests
  ✓ Basic window info
  ✓ Window titles (4 cases)
  ✓ System processes (3 cases)
  ✓ Process errors (4 cases)
  ✓ Window handle zero
  ✓ PID zero
  ✓ Process name none
  ✓ Concurrent window switch
  ✓ Special characters
  ✓ Extended ASCII
  ✓ Multiple parentheses
  ✓ Window API errors (3 cases)
  ✓ Long title