# Unit Tests for S2T-IPA

This directory contains comprehensive unit tests for the Speech-to-Text IPA transcription system.

## Structure

- **`test_json_ipa.py`** - Unit tests for the `JsonIPA` class

  - Tests initialization, token processing, batch processing
  - Tests error handling and edge cases
  - Tests different token fields and data structures

- **`test_wikipron.py`** - Unit tests for the `Wikipron` class

  - Tests dataset loading and caching
  - Tests single and multi-variety pronunciation handling
  - Tests IPA lookup and formatting
  - Tests error handling for missing datasets

- **`test_integration.py`** - Integration tests for the complete system

  - End-to-end processing tests
  - Performance tests with large datasets
  - Unicode handling tests
  - Malformed input handling

- **`conftest.py`** - Test configuration and shared utilities

## Running Tests

### Using uv (recommended)

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_json_ipa.py -v

# Run with coverage
uv run pytest tests/ --cov=app --cov-report=html
```

### Using the test runner script

```bash
# Run all tests
python run_tests.py

# Run specific test file
python run_tests.py test_json_ipa
```

### Using pytest directly (if installed in environment)

```bash
pytest tests/ -v
```

## Test Categories

Tests are marked with the following categories:

- `unit` - Unit tests for individual classes/methods
- `integration` - Integration tests for complete workflows
- `slow` - Tests that take longer to run

Run specific categories:

```bash
# Run only unit tests
uv run pytest tests/ -m unit

# Skip slow tests
uv run pytest tests/ -m "not slow"
```

## Features Tested

✅ **Core Functionality**

- IPA transcription lookup
- Multi-variety pronunciation handling
- Token batch processing
- JSON structure processing

✅ **Error Handling**

- Global error management
- Invalid language codes
- Missing datasets
- Malformed input data

✅ **Performance**

- Caching mechanisms
- Large dataset processing
- Memory efficiency

✅ **Edge Cases**

- Empty inputs
- Unicode characters
- Mixed found/not-found results
- Different token field names

✅ **Data Integrity**

- IPA field omission when no transcription found
- Consistent response structure
- Proper error propagation

## Test Coverage

The tests provide comprehensive coverage of:

- All public methods in `JsonIPA` and `Wikipron` classes
- Error paths and exception handling
- Different input formats and edge cases
- Integration between components

## Adding New Tests

When adding new functionality:

1. Add unit tests in the appropriate test file
2. Add integration tests if the feature affects the complete workflow
3. Follow the existing naming convention: `test_<feature_name>`
4. Use descriptive docstrings for test methods
5. Include both positive and negative test cases

## Dependencies

The tests use:

- `pytest` - Test framework
- `unittest.mock` - Mocking for isolated testing
- Standard library modules for file/path mocking
