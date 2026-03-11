"""
性能测试工具函数
"""

import gc
import os
import time
from typing import Any, Callable, Dict, List, Optional

import psutil


def measure_execution_time(func: Callable, *args, **kwargs) -> tuple[float, Any]:
    """
    测量函数执行时间

    Args:
        func: 要执行的函数
        *args: 函数参数
        **kwargs: 函数关键字参数

    Returns:
        tuple: (执行时间, 函数返回值)
    """
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    return end_time - start_time, result


def run_with_gc(func: Callable, *args, **kwargs) -> Any:
    """
    执行函数并在前后进行垃圾回收

    Args:
        func: 要执行的函数
        *args: 函数参数
        **kwargs: 函数关键字参数

    Returns:
        Any: 函数返回值
    """
    gc.collect()
    result = func(*args, **kwargs)
    gc.collect()
    return result


def generate_test_data() -> Dict[str, List[Any]]:
    """
    生成测试数据

    Returns:
        Dict: 包含不同类型测试数据的字典
    """
    return {
        "numbers": [1, 2, 3, 4, 5, 10, 50, 100],
        "strings": ["test", "performance", "dynamic", "parameter", "benchmark"],
        "dictionaries": [
            {"a": 1, "b": 2},
            {"x": 10, "y": 20},
            {"key1": "value1", "key2": "value2"},
        ],
        "large_dictionaries": [
            {f"key{i}": i for i in range(10)},
            {f"key{i}": i for i in range(50)},
        ],
    }


def validate_performance_threshold(
    execution_time: float, threshold: float, test_name: str
) -> None:
    """
    验证性能是否在阈值内

    Args:
        execution_time: 执行时间
        threshold: 时间阈值
        test_name: 测试名称

    Raises:
        AssertionError: 如果执行时间超过阈值
    """
    assert (
        execution_time < threshold
    ), f"{test_name}执行时间过长: {execution_time:.4f}秒"


def get_current_memory_usage() -> float:
    """
    获取当前进程的内存使用情况

    Returns:
        float: 内存使用量（MB）
    """
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / 1024 / 1024  # 转换为MB


def measure_memory_usage(func: Callable, *args, **kwargs) -> tuple[float, Any]:
    """
    测量函数执行的内存使用情况

    Args:
        func: 要执行的函数
        *args: 函数参数
        **kwargs: 函数关键字参数

    Returns:
        tuple: (内存使用增长, 函数返回值)
    """
    # 执行垃圾回收
    gc.collect()

    # 测量执行前的内存使用
    before_memory = get_current_memory_usage()

    # 执行函数
    result = func(*args, **kwargs)

    # 执行垃圾回收
    gc.collect()

    # 测量执行后的内存使用
    after_memory = get_current_memory_usage()

    # 计算内存使用增长
    memory_increase = after_memory - before_memory

    return memory_increase, result


class TestClass:
    """用于测试对象类型参数的测试类"""

    def __init__(self, value: Any):
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, TestClass):
            return False
        return self.value == other.value


class PerformanceReport:
    """简单的性能报告生成器"""

    def __init__(self):
        self.results = []

    def add_result(
        self,
        test_name: str,
        execution_time: float,
        memory_usage: Optional[float] = None,
    ):
        """
        添加测试结果

        Args:
            test_name: 测试名称
            execution_time: 执行时间（秒）
            memory_usage: 内存使用（MB）
        """
        self.results.append(
            {
                "test_name": test_name,
                "execution_time": execution_time,
                "memory_usage": memory_usage,
            }
        )

    def generate_report(self):
        """
        生成性能报告

        Returns:
            str: 性能报告字符串
        """
        report = "\n===== 性能测试报告 =====\n"

        for result in self.results:
            report += f"测试: {result['test_name']}\n"
            report += f"  执行时间: {result['execution_time']:.6f}秒\n"
            if result["memory_usage"] is not None:
                report += f"  内存使用: {result['memory_usage']:.2f}MB\n"
            report += "\n"

        # 计算平均值
        if self.results:
            avg_time = sum(r["execution_time"] for r in self.results) / len(
                self.results
            )
            report += "===== 统计信息 =====\n"
            report += f"测试总数: {len(self.results)}\n"
            report += f"平均执行时间: {avg_time:.6f}秒\n"

        report += "=====================\n"
        return report

    def print_report(self):
        """
        打印性能报告
        """
        print(self.generate_report())
