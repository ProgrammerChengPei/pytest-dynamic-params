# Performance Tests

Performance tests for pytest-dynamic-params plugin.

## Overview

This directory contains comprehensive performance tests for the pytest-dynamic-params plugin, including:

- **Benchmarks**: Core operation performance benchmarks
- **Caching**: Cache mechanism performance tests
- **Lazy Loading**: Lazy loading performance tests
- **Dependency Resolution**: Dependency resolution performance tests
- **Large-scale Parametrization**: Tests with large parameter sets
- **Memory Efficiency**: Memory usage and leak detection tests
- **Concurrency**: Thread safety and parallel execution tests

## Test Categories

### 1. Benchmarks (`test_benchmarks.py`)

Tests the performance of basic operations:
- Generator creation time
- Generator execution time
- Parametrization overhead
- DynRef creation and resolution
- Decorator application time

**Run**:
```bash
pytest tests/performance/test_benchmarks.py -v
```

### 2. Caching Performance (`test_caching_performance.py`)

Tests caching mechanisms:
- Cache hit/miss performance
- Different scope caching (function, module, session)
- Cache invalidation performance
- Memory usage of caches
- Cache vs no-cache comparison

**Run**:
```bash
pytest tests/performance/test_caching_performance.py -v
```

### 3. Lazy Loading Performance (`test_lazy_loading_performance.py`)

Tests lazy loading mechanisms:
- Lazy load initialization
- Lazy loading with caching
- Deferred execution benefits
- Memory efficiency of lazy loading
- Common lazy loading patterns

**Run**:
```bash
pytest tests/performance/test_lazy_loading_performance.py -v
```

### 4. Dependency Resolution (`test_dependency_resolution.py`)

Tests dependency resolution performance:
- Dependency graph construction
- Cycle detection performance
- Topological sorting
- DynRef resolution
- Complex dependency chains

**Run**:
```bash
pytest tests/performance/test_dependency_resolution.py -v
```

### 5. Large-scale Parametrization (`test_large_scale_parametrization.py`)

Tests performance with large parameter sets:
- Large parameter sets (100, 1000, 10000+ parameters)
- Combinatorial parametrization
- Generator scaling
- Memory usage with large parametrization
- Stress tests

**Run**:
```bash
pytest tests/performance/test_large_scale_parametrization.py -v
```

### 6. Memory Efficiency (`test_memory_efficiency.py`)

Tests memory usage patterns:
- Memory consumption of operations
- Memory leak detection
- Garbage collection behavior
- Memory efficiency optimizations
- Common memory usage patterns

**Run**:
```bash
pytest tests/performance/test_memory_efficiency.py -v
```

### 7. Concurrency (`test_concurrency.py`)

Tests concurrent execution:
- Thread safety
- Parallel execution
- pytest-xdist compatibility
- Distributed caching simulation
- Scalability tests

**Run**:
```bash
pytest tests/performance/test_concurrency.py -v
```

## Running All Performance Tests

### Basic Run

```bash
pytest tests/performance/ -v
```

### With Coverage

```bash
pytest tests/performance/ -v --cov=dynamic_params
```

### With Timing Information

```bash
pytest tests/performance/ -v --durations=10
```

### Generate Reports

```bash
python tests/performance/test_runner.py
```

This will generate:
- `performance_report.json`: JSON format report
- `performance_report.md`: Markdown format report

## Performance Thresholds

The tests use the following performance thresholds:

| Operation | Threshold |
|-----------|-----------|
| Cache hit | < 1ms |
| Cache miss | < 10ms |
| Lazy load | < 5ms |
| Dependency resolve | < 10ms |
| Small param generation | < 50ms |
| Medium param generation | < 200ms |
| Large param generation | < 1000ms |
| Memory usage | < 100MB |

## Benchmark Configuration

Benchmarks can be configured via fixtures in `conftest.py`:

```python
@pytest.fixture(scope="session")
def benchmark_config():
    return {
        "warmup_iterations": 3,
        "benchmark_iterations": 10,
        "sample_size": 100,
        "large_sample_size": 10000,
        "stress_sample_size": 100000,
    }
```

## Performance Optimization Tips

Based on the test results, here are some optimization tips:

### 1. Use Caching

```python
# Good: Use caching for expensive operations
@param_generator(cache=True, scope="session")
def generate_expensive_data():
    time.sleep(1)  # Expensive operation
    return list(range(1000))
```

### 2. Use Lazy Loading

```python
# Good: Use lazy loading for large datasets
@param_generator(lazy=True, cache=True)
def generate_large_data():
    return list(range(100000))
```

### 3. Choose Appropriate Scope

```python
# Session scope for shared data
@param_generator(cache=True, scope="session")
def generate_shared_data():
    return shared_data

# Function scope for test-specific data
@param_generator(cache=True, scope="function")
def generate_test_data():
    return test_specific_data
```

### 4. Optimize Dependency Resolution

```python
# Good: Minimize dependency depth
# Bad: Deep dependency chains
```

### 5. Monitor Memory Usage

```python
# Good: Clean up large objects
# Good: Use generators for streaming
```

## Interpreting Results

### Test Output

```
test_benchmarks.py::TestGeneratorBenchmarks::test_generator_creation_time PASSED [  1%]
test_benchmarks.py::TestGeneratorBenchmarks::test_simple_generator_execution PASSED [  2%]
...
```

### Performance Report

The generated reports include:
- Total test count
- Pass/fail rates
- Average, min, max durations
- Per-category breakdowns
- Performance highlights

### Thresholds

Tests will fail if they exceed defined thresholds. For example:
- Cache hit should be < 1ms
- Large parametrization should complete in < 1000ms
- Memory usage should be < 100MB

## Troubleshooting

### Tests Failing Due to Performance

If tests fail due to performance thresholds:
1. Check if the test environment is under heavy load
2. Verify that caching is enabled where appropriate
3. Check for memory leaks
4. Consider adjusting thresholds for CI environments

### Memory Issues

If memory usage is high:
1. Use lazy loading for large datasets
2. Clear caches when not needed
3. Use appropriate scope levels
4. Monitor garbage collection

### Concurrency Issues

If concurrent tests fail:
1. Check for race conditions
2. Verify thread safety of custom code
3. Use proper locking mechanisms
4. Test with different thread counts

## Continuous Integration

Performance tests can be integrated into CI pipelines:

```yaml
# .github/workflows/performance.yml
name: Performance Tests

on: [push, pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -e .
      - name: Run performance tests
        run: pytest tests/performance/ -v --durations=10
      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: performance-report
          path: tests/performance/performance_report.md
```

## Contributing

When adding new features, please:
1. Add corresponding performance tests
2. Document performance characteristics
3. Include optimization tips if applicable
4. Update thresholds if necessary

## References

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-benchmark](https://pytest-benchmark.readthedocs.io/)
- [Performance Testing Best Practices](https://docs.pytest.org/en/stable/benchmark.html)
