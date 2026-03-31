# Compatibility Tests for pytest-dynamic-params

This directory contains comprehensive compatibility tests for the pytest-dynamic-params plugin, verifying its compatibility with other pytest plugins and different Python/pytest versions.

## Test Structure

```
tests/compatibility/
├── __init__.py                      # Package initialization
├── conftest.py                      # Shared fixtures and configuration
├── README.md                        # This file
├── test_xdist.py                    # pytest-xdist compatibility tests
├── test_pytest_cov.py               # pytest-cov compatibility tests
├── test_pytest_asyncio.py           # pytest-asyncio compatibility tests
├── test_pytest_bdd.py               # pytest-bdd compatibility tests
└── test_version_compatibility.py    # Python/pytest version compatibility tests
```

## Running Compatibility Tests

### Run All Compatibility Tests

```bash
pytest tests/compatibility/ -v
```

### Run Specific Plugin Compatibility Tests

#### pytest-xdist Compatibility

```bash
pytest tests/compatibility/test_xdist.py -v
```

#### pytest-cov Compatibility

```bash
pytest tests/compatibility/test_pytest_cov.py -v
```

#### pytest-asyncio Compatibility

```bash
pytest tests/compatibility/test_pytest_asyncio.py -v
```

#### pytest-bdd Compatibility

```bash
pytest tests/compatibility/test_pytest_bdd.py -v
```

#### Version Compatibility

```bash
pytest tests/compatibility/test_version_compatibility.py -v
```

## Compatibility Matrix

| Plugin | Status | Notes |
|--------|--------|-------|
| pytest-xdist | ✅ Tested | Parallel execution, distributed caching, load balancing |
| pytest-cov | ✅ Tested | Coverage reports (term, html, xml) |
| pytest-asyncio | ✅ Tested | Async test functions, async fixtures |
| pytest-bdd | ✅ Tested | BDD scenarios, outline scenarios |

## Test Categories

### 1. pytest-xdist Compatibility (`test_xdist.py`)

Tests compatibility with pytest-xdist for parallel test execution:

- **Basic Compatibility**: Parallel execution with dynamic params
- **Distributed Caching**: Cache consistency across workers
- **Load Balancing**: Proper distribution of parametrized tests
- **Edge Cases**: Lazy loading, nested generators, single worker mode
- **Stress Tests**: High volume parallel execution

**Key Features Tested:**
- ✅ Parallel execution with generators
- ✅ DynRef in parallel mode
- ✅ Fixture parametrization with xdist
- ✅ Session-scoped caching across workers
- ✅ Load balancing with many test cases

### 2. pytest-cov Compatibility (`test_pytest_cov.py`)

Tests compatibility with pytest-cov for coverage measurement:

- **Basic Compatibility**: Coverage with dynamic params
- **DynRef Coverage**: Coverage tracking with DynRef
- **Fixture Coverage**: Coverage with parametrized fixtures
- **Caching**: Coverage with cached generators
- **Report Generation**: HTML, XML, and term reports

**Key Features Tested:**
- ✅ Coverage measurement with generators
- ✅ Coverage with DynRef expressions
- ✅ Multiple report formats
- ✅ Caching and lazy loading coverage

### 3. pytest-asyncio Compatibility (`test_pytest_asyncio.py`)

Tests compatibility with pytest-asyncio for async test functions:

- **Basic Compatibility**: Async tests with dynamic params
- **DynRef with Async**: DynRef in async context
- **Async Fixtures**: Parametrized async fixtures
- **Caching**: Async tests with cached generators
- **Concurrent Execution**: Multiple async tests

**Key Features Tested:**
- ✅ Async test functions with parametrization
- ✅ Async fixtures with dynamic params
- ✅ Generator-based async parametrization
- ✅ Concurrent async test execution

### 4. pytest-bdd Compatibility (`test_pytest_bdd.py`)

Tests compatibility with pytest-bdd for BDD-style tests:

- **Basic Compatibility**: BDD scenarios with dynamic params
- **DynRef with BDD**: DynRef in BDD context
- **Fixture Integration**: Parametrized fixtures in BDD
- **Outline Scenarios**: Compatibility with scenario outlines

**Key Features Tested:**
- ✅ BDD scenarios with parametrization
- ✅ Generator usage in BDD tests
- ✅ Mixed BDD and parametrized tests

### 5. Version Compatibility (`test_version_compatibility.py`)

Tests compatibility across different Python and pytest versions:

- **Python Versions**: 3.7, 3.8, 3.9, 3.10+ features
- **Pytest Versions**: pytest 7.0+ features
- **Core Functionality**: Dynamic params core features
- **Type Hints**: Type annotation compatibility
- **Import/Export**: Module import compatibility

**Key Features Tested:**
- ✅ Python version-specific features
- ✅ Pytest version compatibility
- ✅ Type hint compatibility
- ✅ Error handling across versions

## Test Infrastructure

### Fixtures

The `conftest.py` provides shared fixtures:

- `test_dir`: Test directory path
- `root_dir`: Project root directory path
- `isolated_test_env`: Isolated test environment
- `pytest_runner`: Run pytest in subprocess
- `python_version`: Current Python version
- `pytest_version`: Current pytest version

### Running Tests in Isolation

Tests use isolated environments to avoid interference:

```python
def test_example(isolated_test_env, pytest_runner):
    test_file = isolated_test_env / "test_example.py"
    test_file.write_text("""
        # Test code here
    """)
    
    result = pytest_runner(
        test_file,
        args=["-v"],
        cwd=isolated_test_env
    )
    
    assert result["success"]
```

## Requirements

To run all compatibility tests, install the following optional dependencies:

```bash
pip install pytest-xdist
pip install pytest-cov
pip install pytest-asyncio
pip install pytest-bdd
```

## Known Limitations

1. **pytest-xdist**: Distributed caching may have limitations with certain cache configurations
2. **pytest-asyncio**: Requires `--asyncio-mode=auto` or `--asyncio-mode=strict` flag
3. **pytest-bdd**: Some BDD features may not fully integrate with dynamic parametrization

## Contributing

When adding new compatibility tests:

1. Follow the existing test structure
2. Use the `isolated_test_env` fixture for isolation
3. Test both basic usage and edge cases
4. Document any known limitations
5. Update this README with new test categories

## Troubleshooting

### Common Issues

**Issue**: Tests fail with "plugin not found"
- **Solution**: Install the required plugin: `pip install pytest-<plugin-name>`

**Issue**: Coverage reports not generated
- **Solution**: Ensure pytest-cov is installed and `--cov` flag is used

**Issue**: Async tests don't run
- **Solution**: Add `--asyncio-mode=auto` flag or mark tests with `@pytest.mark.asyncio`

**Issue**: Parallel tests hang
- **Solution**: Reduce worker count or check for deadlocks in generator code

## Performance Notes

- Compatibility tests may take longer to run than unit tests
- pytest-xdist tests spawn multiple subprocesses
- Coverage tests generate report files
- Async tests have inherent overhead from event loop

## Future Work

Planned compatibility tests:

- [ ] pytest-mock compatibility
- [ ] pytest-django compatibility
- [ ] pytest-flask compatibility
- [ ] pytest-aiohttp compatibility
- [ ] More Python version specific tests
- [ ] pytest 8.0+ compatibility tests

## References

- [pytest-xdist Documentation](https://pytest-xdist.readthedocs.io/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [pytest-bdd Documentation](https://pytest-bdd.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
