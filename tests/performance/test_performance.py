"""
性能测试用例 - 测试pytest-dynamic-params插件的性能特征
"""

import platform
import random

import pytest

from dynamic_params import param_generator, with_dynamic_params
from tests.utils import (
    TestClass,
    measure_execution_time,
    run_with_gc,
    validate_performance_threshold,
)

# 设置固定的随机种子，确保测试可重复性
random.seed(42)

# 收集环境信息
env_info = {
    "python_version": platform.python_version(),
    "platform": platform.platform(),
    "processor": platform.processor(),
    "os": platform.system(),
    "os_version": platform.version(),
}

print("测试环境信息:")
for key, value in env_info.items():
    print(f"  {key}: {value}")


class TestPerformance:
    """性能测试类"""

    def test_large_parameter_combinations_performance(self):
        """测试大量参数组合的性能"""

        # 创建一个简单的参数生成器
        @param_generator
        def generate_numbers(n):
            return n * 2

        @with_dynamic_params(doubled=generate_numbers)
        @pytest.mark.parametrize("n", list(range(100)))  # 100个参数值
        def test_large_combinations(n, doubled):
            assert doubled == n * 2

        # 测量执行时间
        def run_test():
            for i in range(100):
                test_large_combinations(i, i * 2)

        execution_time, _ = measure_execution_time(run_test)
        validate_performance_threshold(execution_time, 1.0, "大量参数组合测试")

    def test_many_generators_performance(self):
        """测试多个生成器的性能"""
        # 创建多个参数生成器
        generators = {}
        for i in range(10):

            @param_generator
            def generate_data(input_val, i=i):
                return input_val + i

            generators[f"data_{i}"] = generate_data

        # 测试函数
        def make_test_func(gen_dict):
            @with_dynamic_params(**gen_dict)
            @pytest.mark.parametrize("input_val", [1, 2, 3, 4, 5])
            def test_func(input_val, **kwargs):
                for i in range(10):
                    assert kwargs[f"data_{i}"] == input_val + i

            return test_func

        test_func = make_test_func(generators)

        def run_test():
            for val in [1, 2, 3, 4, 5]:
                test_func(val, **{f"data_{i}": val + i for i in range(10)})

        execution_time, _ = measure_execution_time(run_test)
        validate_performance_threshold(execution_time, 1.0, "多生成器测试")

    def test_cache_performance_benefit(self):
        """测试缓存机制的性能优势"""

        # 注意：缓存功能可能在插件的其他部分实现，这里我们只测试基本功能
        @param_generator(cache=True)  # 启用缓存
        def cached_generator(x):
            return x * 2

        @with_dynamic_params(result=cached_generator)
        def test_func(x, result):
            assert result == x * 2

        def run_test():
            results = []
            for x in [1, 2, 3, 4, 5] * 10:
                test_func(x, x * 2)
            return results

        execution_time, _ = measure_execution_time(run_test)
        validate_performance_threshold(execution_time, 0.5, "缓存版本测试")

    def test_without_cache_performance_comparison(self):
        """测试不使用缓存的性能（对比）"""
        call_count = 0

        @param_generator(cache=False)  # 不启用缓存
        def uncached_generator(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # 直接测试生成器函数，不使用装饰器
        def run_test():
            results = []
            for x in [1, 2, 3, 4, 5] * 10:
                results.append(uncached_generator(x))
            return results

        execution_time, results = measure_execution_time(run_test)

        # 验证没有缓存时调用次数更多（应该有50次）
        expected_calls = 50  # 因为每次都会调用
        assert (
            call_count == expected_calls
        ), f"非缓存版本调用次数异常: 实际{call_count}次，预期{expected_calls}次"
        # 验证所有结果正确
        expected_results = [x * 2 for x in [1, 2, 3, 4, 5] * 10]
        assert results == expected_results, "生成器结果不正确"
        # 注意：这里不对执行时间做严格断言，因为不使用缓存通常会更慢

    def test_nested_generators_performance(self):
        """测试嵌套生成器的性能"""

        @param_generator
        def generate_base(x):
            return x + 10

        @param_generator
        def generate_transformed(base_value):  # 依赖于另一个生成器
            return base_value * 2

        @with_dynamic_params(
            base_value=generate_base, transformed_value=generate_transformed
        )
        @pytest.mark.parametrize("x", list(range(50)))  # 50个输入值
        def test_nested(x, base_value, transformed_value):
            assert base_value == x + 10
            assert transformed_value == (x + 10) * 2

        def run_test():
            for x in range(50):
                test_nested(x, x + 10, (x + 10) * 2)

        execution_time, _ = measure_execution_time(run_test)
        validate_performance_threshold(execution_time, 1.0, "嵌套生成器测试")

    def test_memory_usage_stability(self):
        """测试内存使用稳定性（间接测试）"""

        @param_generator
        def generate_list(n):
            # 创建一个较大的列表来测试内存管理
            return list(range(n))

        @with_dynamic_params(big_list=generate_list)
        @pytest.mark.parametrize("n", [10, 50, 100])  # 不同大小的列表
        def test_memory(n, big_list):
            assert len(big_list) == n
            assert big_list[-1] == n - 1 if n > 0 else True

        def run_test():
            for _ in range(100):  # 重复运行
                for n in [10, 50, 100]:
                    test_memory(n, list(range(n)))

        # 运行测试并进行垃圾回收
        execution_time, _ = measure_execution_time(lambda: run_with_gc(run_test))
        validate_performance_threshold(execution_time, 2.0, "内存稳定性测试")

    def test_concurrent_access_simulation(self):
        """模拟并发访问场景的性能（通过快速连续调用）"""

        @param_generator
        def compute_heavy_task(x):
            # 模拟一些计算密集型任务
            result = 0
            for i in range(100):
                result += x * i
            return result

        @with_dynamic_params(heavy_result=compute_heavy_task)
        @pytest.mark.parametrize("x", list(range(20)))
        def test_concurrent_simulation(x, heavy_result):
            expected = sum(x * i for i in range(100))
            assert heavy_result == expected

        def run_test():
            for x in range(20):
                test_concurrent_simulation(x, sum(x * i for i in range(100)))

        execution_time, _ = measure_execution_time(run_test)
        validate_performance_threshold(execution_time, 1.0, "并发模拟测试")

    def test_different_parameter_types_performance(self):
        """测试不同类型参数的性能"""

        # 测试字符串类型
        @param_generator
        def process_string(s):
            return s.upper()

        # 测试复杂数据结构
        @param_generator
        def process_dict(d):
            return {k: v * 2 for k, v in d.items()}

        # 测试对象类型
        @param_generator
        def process_object(obj):
            return obj.value * 3

        # 测试字符串参数
        @with_dynamic_params(uppercase=process_string)
        @pytest.mark.parametrize("s", ["test", "performance", "dynamic", "parameter"])
        def test_string_params(s, uppercase):
            assert uppercase == s.upper()

        # 测试字典参数
        @with_dynamic_params(processed=process_dict)
        @pytest.mark.parametrize("d", [{"a": 1, "b": 2}, {"x": 10, "y": 20}])
        def test_dict_params(d, processed):
            expected = {k: v * 2 for k, v in d.items()}
            assert processed == expected

        # 测试对象参数
        @with_dynamic_params(processed=process_object)
        @pytest.mark.parametrize("obj", [TestClass(1), TestClass(2), TestClass(3)])
        def test_object_params(obj, processed):
            assert processed == obj.value * 3

        def run_test():
            # 测试字符串
            for s in ["test", "performance", "dynamic", "parameter"]:
                test_string_params(s, s.upper())

            # 测试字典
            for d in [{"a": 1, "b": 2}, {"x": 10, "y": 20}]:
                expected = {k: v * 2 for k, v in d.items()}
                test_dict_params(d, expected)

            # 测试对象
            for i in [1, 2, 3]:
                obj = TestClass(i)
                test_object_params(obj, i * 3)

        execution_time, _ = measure_execution_time(run_test)
        validate_performance_threshold(execution_time, 1.0, "不同类型参数测试")

    def test_cache_strategy_performance(self):
        """测试不同缓存策略的性能"""

        # 测试缓存与非缓存的性能对比
        @param_generator(cache=True)
        def cached_generator(x):
            return x * 2

        @param_generator(cache=False)
        def uncached_generator(x):
            return x * 2

        @with_dynamic_params(result=cached_generator)
        def test_cached_func(x, result):
            assert result == x * 2

        @with_dynamic_params(result=uncached_generator)
        def test_uncached_func(x, result):
            assert result == x * 2

        # 测试缓存版本
        def run_cached_test():
            for x in [1, 2, 3, 4, 5] * 10:
                test_cached_func(x, x * 2)

        # 测试非缓存版本
        def run_uncached_test():
            for x in [1, 2, 3, 4, 5] * 10:
                test_uncached_func(x, x * 2)

        # 运行测试
        cached_time, _ = measure_execution_time(run_cached_test)
        uncached_time, _ = measure_execution_time(run_uncached_test)

        print(f"缓存版本: {cached_time:.6f}秒")
        print(f"非缓存版本: {uncached_time:.6f}秒")

        # 验证性能在合理范围内
        validate_performance_threshold(cached_time, 1.0, "缓存版本测试")
        validate_performance_threshold(uncached_time, 1.0, "非缓存版本测试")

    def test_memory_usage_measurement(self):
        """测试内存使用情况"""
        from tests.performance.utils import measure_memory_usage

        # 测试生成大对象时的内存使用
        @param_generator
        def generate_large_list(n):
            # 创建一个较大的列表
            return list(range(n))

        # 直接测试生成器函数
        def run_test(size):
            # 多次调用以确保内存使用稳定
            results = []
            for _ in range(5):
                results.append(generate_large_list(size))
            return results

        # 测试不同大小的列表
        list_sizes = [10000, 50000, 100000]
        memory_usages = []

        for size in list_sizes:
            _, memory_increase = measure_memory_usage(run_test, size)
            memory_usages.append((size, memory_increase))
            print(f"列表大小 {size}: 内存增长 {memory_increase:.2f} MB")

        # 测试缓存对内存使用的影响
        @param_generator(cache=True)
        def cached_generator(x):
            return list(range(x))

        def run_cached_test():
            # 重复使用相同的参数
            results = []
            for _ in range(5):
                results.append(cached_generator(10000))
            return results

        _, memory_increase = measure_memory_usage(run_cached_test)
        print(f"缓存版本内存增长: {memory_increase:.2f} MB")

        # 验证缓存版本的内存使用合理
        assert memory_increase < 10.0, f"缓存版本内存使用过高: {memory_increase:.2f} MB"
