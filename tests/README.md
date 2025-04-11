# ActionMan Test Suite

This directory contains the test suite for the ActionMan build tool. The tests are organized into unit tests for individual components and integration tests that verify the complete workflow.

## Test Structure

- `conftest.py`: Contains shared fixtures used across test modules
- `test_*.py`: Individual test modules for each component

## Running Tests

To run the complete test suite:

```bash
python -m pytest
```

To run a specific test module:

```bash
python -m pytest tests/test_core.py
```

To run tests with a specific marker:

```bash
python -m pytest -m unit  # Run only unit tests
python -m pytest -m integration  # Run only integration tests
```

## Test Coverage

The test suite covers the following components:

- **Core Module**: Tests for the BuildManager class, which serves as a facade for all operations
- **Build Operations**: Tests for configuring, building, and installing C++ projects
- **Run Operations**: Tests for finding and running built executables
- **Test Operations**: Tests for running tests on built executables
- **System Operations**: Tests for displaying system information and help
- **Integration Tests**: End-to-end tests that verify the complete workflow

## Adding New Tests

When adding new tests, follow these guidelines:

1. Create a new test module in the `tests` directory with the name `test_*.py`
2. Use the fixtures defined in `conftest.py` where appropriate
3. Add unit tests for individual functions and methods
4. Add integration tests for complete workflows
5. Use mocking to avoid executing real commands during tests

## Test Fixtures

The test suite provides the following fixtures:

- `temp_dir`: Creates a temporary directory for tests
- `mock_build_dir`: Creates a mock build directory structure
- `build_operations`: Creates a BuildOperations instance
- `run_operations`: Creates a RunOperations instance
- `test_operations`: Creates a TestOperations instance
- `system_operations`: Creates a SystemOperations instance
- `build_manager`: Creates a BuildManager instance
- `mock_command_runner`: Mocks the run_command function to avoid executing real commands
