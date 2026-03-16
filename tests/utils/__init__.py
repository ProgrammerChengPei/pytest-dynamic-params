"""
测试工具模块
提供共享的测试工具函数和fixture
"""

from .assertions import assert_cached_value, assert_error_message, assert_lazy_result
from .data import create_test_data
from .fixtures import test_list, test_value
from .generators import (
    cached_generator,
    dependency_generator,
    failing_generator,
    lazy_generator,
)
from .performance import (
    PerformanceReport,
    TestClass,
    generate_test_data,
    get_current_memory_usage,
    measure_execution_time,
    measure_memory_usage,
    run_with_gc,
    validate_performance_threshold,
)

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
