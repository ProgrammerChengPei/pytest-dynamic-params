"""
测试工具模块
提供共享的测试工具函数和fixture
"""

from .generators import (
    failing_generator,
    dependency_generator,
    cached_generator,
    lazy_generator,
)

from .assertions import (
    assert_error_message,
    assert_cached_value,
    assert_lazy_result
)

from .performance import (
    measure_execution_time,
    run_with_gc,
    generate_test_data,
    validate_performance_threshold,
    get_current_memory_usage,
    measure_memory_usage,
    TestClass,
    PerformanceReport,
)

from .fixtures import test_value, test_list

from .data import create_test_data

__all__ = [
    # Generators
    "failing_generator",
    "dependency_generator",
    "cached_generator",
    "lazy_generator",
    # Assertions
    "assert_error_message",
    "assert_cached_value",
    "assert_lazy_result",
    # Performance
    "measure_execution_time",
    "run_with_gc",
    "generate_test_data",
    "validate_performance_threshold",
    "get_current_memory_usage",
    "measure_memory_usage",
    "TestClass",
    "PerformanceReport",
    # Fixtures
    "test_value",
    "test_list",
    # Data
    "create_test_data",
]
