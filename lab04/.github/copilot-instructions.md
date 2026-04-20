# Project Coding Conventions

## Python Style
- Use `pathlib.Path` instead of `os.path` for all file operations
- Use `dataclasses` for configuration objects, `Pydantic` for user input validation
- All functions must have type hints for parameters and return values
- Use Google-style docstrings with Args, Returns, and Raises sections

## Testing
- Use `pytest` with fixtures — no `unittest.TestCase`
- Use factory fixtures (fixture returns a function) for test data
- Use `tmp_path` fixture for file system tests — never write to real directories
- Use `pytest.mark.parametrize` for data-driven tests
- Name test files `test_<module>.py`, test functions `test_<behavior>()`

## Error Handling
- Use custom exception classes, not generic `Exception`
- Always log errors before raising
- Return result objects (dicts with status) instead of raising in public APIs

## Naming
- snake_case for functions and variables
- PascalCase for classes
- UPPER_CASE for constants
- Prefix private methods with underscore
