"""
性能基准测试 - 为pytest-dynamic-params插件建立性能基线
"""

import time

import pytest

from dynamic_params import param_generator, with_dynamic_params


class TestPerformanceBenchmark:
    """性能基准测试类"""

    def test_baseline_performance(self):
        """基线性能测试 - 最简单场景"""

        @param_generator
        def simple_return(x):
            return x

        @with_dynamic_params(result=simple_return)
        @pytest.mark.parametrize("x", [1, 2, 3])
        def test_simple_case(x, result):
            assert result == x

        start_time = time.perf_counter()
        for x in [1, 2, 3]:
            test_simple_case(x, x)
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        print(f"基线测试执行时间: {execution_time:.6f}秒")

        # 设置合理的基线时间阈值
        assert execution_time < 0.1, f"基线测试超时: {execution_time:.6f}秒"

    def test_scaling_with_parameter_count(self):
        """测试随参数数量增长的性能变化"""
        execution_times = []

        for param_size in [10, 50, 100]:  # 不同参数数量

            @param_generator
            def identity_func(x):
                return x

            @with_dynamic_params(output=identity_func)
            @pytest.mark.parametrize("x", list(range(param_size)))
            def test_scaling(x, output):
                assert output == x

            start_time = time.perf_counter()
            for x in range(param_size):
                test_scaling(x, x)
            end_time = time.perf_counter()

            execution_time = end_time - start_time
            execution_times.append((param_size, execution_time))
            print(f"参数数量 {param_size}: {execution_time:.6f}秒")

        # 验证执行时间随参数数量合理增长
        # （不应出现指数级增长）
        if len(execution_times) >= 2:
            smaller_time = execution_times[0][1]
            larger_time = execution_times[-1][1]
            # 假设100个参数的时间不应超过10个参数的20倍
            assert larger_time / smaller_time < 20, "性能扩展不佳: 时间增长过多"

    def test_generator_complexity_impact(self):
        """测试生成器复杂度对性能的影响"""

        # 简单生成器
        @param_generator
        def simple_gen(x):
            return x + 1

        # 中等复杂度生成器
        @param_generator
        def medium_gen(x):
            result = 0
            for i in range(x % 10 + 1):
                result += i * 2
            return result

        # 高复杂度生成器
        @param_generator
        def complex_gen(x):
            result = []
            for i in range(min(x, 20)):
                inner_sum = sum(j * j for j in range(i + 1))
                result.append(inner_sum)
            return result

        # 测试简单生成器性能
        @with_dynamic_params(output=simple_gen)
        @pytest.mark.parametrize("x", list(range(20)))
        def test_simple_gen_perf(x, output):
            assert output == x + 1

        start_time = time.perf_counter()
        for x in range(20):
            test_simple_gen_perf(x, x + 1)
        simple_time = time.perf_counter() - start_time

        # 测试中等复杂度生成器性能
        @with_dynamic_params(output=medium_gen)
        @pytest.mark.parametrize("x", list(range(20)))
        def test_medium_gen_perf(x, output):
            expected = sum(i * 2 for i in range(x % 10 + 1))
            assert output == expected

        start_time = time.perf_counter()
        for x in range(20):
            test_medium_gen_perf(x, sum(i * 2 for i in range(x % 10 + 1)))
        medium_time = time.perf_counter() - start_time

        # 测试高复杂度生成器性能
        @with_dynamic_params(output=complex_gen)
        @pytest.mark.parametrize("x", list(range(10)))  # 减少数量以避免过长时间
        def test_complex_gen_perf(x, output):
            expected = [sum(j * j for j in range(i + 1)) for i in range(min(x, 20))]
            assert output == expected

        start_time = time.perf_counter()
        for x in range(10):
            expected = [sum(j * j for j in range(i + 1)) for i in range(min(x, 20))]
            test_complex_gen_perf(x, expected)
        complex_time = time.perf_counter() - start_time

        print(f"简单生成器时间: {simple_time:.6f}秒")
        print(f"中等复杂度生成器时间: {medium_time:.6f}秒")
        print(f"高复杂度生成器时间: {complex_time:.6f}秒")

        # 验证复杂度增加导致的时间增加是合理的
        assert medium_time >= simple_time, "中等复杂度应该比简单复杂度耗时更长"
        assert complex_time >= medium_time, "高复杂度应该比中等复杂度耗时更长"

    def test_cache_effectiveness_measurement(self):
        """测量缓存机制的有效性"""

        # 注意：缓存功能可能在插件的其他部分实现，这里我们只测试基本功能
        @param_generator(cache=True)
        def gen_with_cache(x):
            return x * 2

        @param_generator(cache=False)
        def gen_without_cache(x):
            return x * 2

        # 测试带缓存的版本
        @with_dynamic_params(result=gen_with_cache)
        @pytest.mark.parametrize("x", [1, 2, 1, 3, 2, 1])  # 有重复值
        def test_with_cache(x, result):
            assert result == x * 2

        start_time = time.perf_counter()
        for x in [1, 2, 1, 3, 2, 1]:
            test_with_cache(x, x * 2)
        with_cache_time = time.perf_counter() - start_time

        # 测试不带缓存的版本
        @with_dynamic_params(result=gen_without_cache)
        @pytest.mark.parametrize("x", [1, 2, 1, 3, 2, 1])  # 相同的重复值
        def test_without_cache(x, result):
            assert result == x * 2

        start_time = time.perf_counter()
        for x in [1, 2, 1, 3, 2, 1]:
            test_without_cache(x, x * 2)
        without_cache_time = time.perf_counter() - start_time

        print("带缓存版本:")
        print(f"  执行时间: {with_cache_time:.6f}秒")

        print("不带缓存版本:")
        print(f"  执行时间: {without_cache_time:.6f}秒")

        # 验证性能在合理范围内
        assert with_cache_time < 1.0, f"缓存版本执行时间过长: {with_cache_time:.6f}秒"
        assert (
            without_cache_time < 1.0
        ), f"非缓存版本执行时间过长: {without_cache_time:.6f}秒"

    def test_dependency_chain_performance(self):
        """测试依赖链的性能"""

        # 创建一个依赖链: gen_a -> gen_b -> gen_c
        @param_generator
        def gen_a(x):
            return x + 1

        @param_generator
        def gen_b(a_result):
            return a_result * 2

        @param_generator
        def gen_c(b_result):
            return b_result - 1

        @with_dynamic_params(a_result=gen_a, b_result=gen_b, c_result=gen_c)
        @pytest.mark.parametrize("x", list(range(30)))
        def test_deps(x, a_result, b_result, c_result):
            assert a_result == x + 1
            assert b_result == (x + 1) * 2
            assert c_result == (x + 1) * 2 - 1

        start_time = time.perf_counter()
        for x in range(30):
            expected_a = x + 1
            expected_b = (x + 1) * 2
            expected_c = (x + 1) * 2 - 1
            test_deps(x, expected_a, expected_b, expected_c)
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        print(f"依赖链测试执行时间: {execution_time:.6f}秒")

        assert execution_time < 1.0, f"依赖链性能过低: {execution_time:.6f}秒"
