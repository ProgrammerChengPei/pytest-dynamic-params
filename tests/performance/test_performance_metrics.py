"""
性能测试用例 - 测试pytest-dynamic-params插件的性能指标
"""

import random

from dynamic_params import dynamic_params, param_generator
from tests.utils import (
    measure_execution_time,
    run_with_gc,
    validate_performance_threshold,
)

# 设置固定的随机种子，确保测试可重复性
random.seed(42)


class TestPerformanceMetrics:
    """性能指标测试类"""

    def test_different_scopes_performance(self):
        """测试不同作用域下的性能"""
        # 测试不同作用域的生成器
        scopes = ["function", "class", "module", "session"]
        times = {}

        for scope in scopes:

            @param_generator(scope=scope)
            def generate_value(x):
                return x * 2

            @dynamic_params(value=generate_value)
            def test_func(x, value):
                assert value == x * 2

            def run_test():
                for x in range(100):
                    test_func(x, x * 2)

            execution_time, _ = measure_execution_time(run_test)
            times[scope] = execution_time
            print(f"作用域 {scope}: {execution_time:.6f}秒")

        # 验证所有作用域的性能都在合理范围内
        for scope, time_taken in times.items():
            validate_performance_threshold(time_taken, 1.0, f"作用域 {scope} 测试")

    def test_lazy_vs_eager_performance(self):
        """测试懒加载与非懒加载的性能对比"""

        # 测试懒加载模式
        @param_generator(lazy=True)
        def lazy_generator(x):
            # 模拟一些计算
            result = 0
            for i in range(100):
                result += x * i
            return result

        # 测试非懒加载模式
        @param_generator(lazy=False)
        def eager_generator(x):
            # 模拟一些计算
            result = 0
            for i in range(100):
                result += x * i
            return result

        @dynamic_params(value=lazy_generator)
        def test_lazy_func(x, value):
            assert value == sum(x * i for i in range(100))

        @dynamic_params(value=eager_generator)
        def test_eager_func(x, value):
            assert value == sum(x * i for i in range(100))

        # 运行懒加载测试
        def run_lazy_test():
            for x in range(50):
                test_lazy_func(x, sum(x * i for i in range(100)))

        # 运行非懒加载测试
        def run_eager_test():
            for x in range(50):
                test_eager_func(x, sum(x * i for i in range(100)))

        lazy_time, _ = measure_execution_time(run_lazy_test)
        eager_time, _ = measure_execution_time(run_eager_test)

        print(f"懒加载模式: {lazy_time:.6f}秒")
        print(f"非懒加载模式: {eager_time:.6f}秒")

        # 验证性能在合理范围内
        validate_performance_threshold(lazy_time, 1.0, "懒加载模式测试")
        validate_performance_threshold(eager_time, 1.0, "非懒加载模式测试")

    def test_complex_dependency_chain_performance(self):
        """测试复杂依赖链的性能"""

        # 创建深层依赖链
        @param_generator
        def level1(x):
            return x + 1

        @param_generator
        def level2(level1):
            return level1 * 2

        @param_generator
        def level3(level2):
            return level2 + 3

        @param_generator
        def level4(level3):
            return level3 * 4

        @param_generator
        def level5(level4):
            return level4 + 5

        @dynamic_params(
            level1=level1, level2=level2, level3=level3, level4=level4, level5=level5
        )
        def test_complex_chain(x, level1, level2, level3, level4, level5):
            assert level1 == x + 1
            assert level2 == (x + 1) * 2
            assert level3 == (x + 1) * 2 + 3
            assert level4 == ((x + 1) * 2 + 3) * 4
            assert level5 == ((x + 1) * 2 + 3) * 4 + 5

        def run_test():
            for x in range(30):
                l1 = x + 1
                l2 = l1 * 2
                l3 = l2 + 3
                l4 = l3 * 4
                l5 = l4 + 5
                test_complex_chain(x, l1, l2, l3, l4, l5)

        execution_time, _ = measure_execution_time(run_test)
        validate_performance_threshold(execution_time, 1.0, "复杂依赖链测试")

    def test_long_running_stability(self):
        """测试长时间运行的稳定性"""

        @param_generator(cache=True)
        def stable_generator(x):
            return x * 10

        @dynamic_params(value=stable_generator)
        def test_stable_func(x, value):
            assert value == x * 10

        def run_test():
            for _ in range(500):  # 运行500次
                for x in range(10):
                    test_stable_func(x, x * 10)

        execution_time, _ = measure_execution_time(lambda: run_with_gc(run_test))
        validate_performance_threshold(execution_time, 3.0, "长时间运行稳定性测试")

    def test_generator_initialization_performance(self):
        """测试生成器初始化性能"""

        def create_and_test_generator():
            @param_generator
            def test_generator(x):
                return x + 1

            @dynamic_params(value=test_generator)
            def test_func(x, value):
                assert value == x + 1

            # 运行一次测试
            test_func(1, 2)

        # 多次创建和测试生成器
        def run_test():
            for _ in range(100):
                create_and_test_generator()

        execution_time, _ = measure_execution_time(run_test)
        validate_performance_threshold(execution_time, 1.0, "生成器初始化性能测试")

    def test_parameter_validation_performance(self):
        """测试参数验证性能"""

        @param_generator
        def generator_with_validation(x):
            if not isinstance(x, int):
                raise ValueError("必须是整数")
            return x * 2

        @dynamic_params(value=generator_with_validation)
        def test_validation_func(x, value):
            assert value == x * 2

        def run_test():
            for x in range(50):
                test_validation_func(x, x * 2)

        execution_time, _ = measure_execution_time(run_test)
        validate_performance_threshold(execution_time, 1.0, "参数验证性能测试")

    def test_error_handling_performance(self):
        """测试错误处理性能"""

        @param_generator
        def error_generator(x):
            if x == 0:
                raise ValueError("不能为零")
            return 10 / x

        @dynamic_params(value=error_generator)
        def test_error_func(x, value):
            if x == 0:
                assert value is None
            else:
                assert value == 10 / x

        def run_test():
            for x in range(0, 10):
                if x == 0:
                    test_error_func(x, None)
                else:
                    test_error_func(x, 10 / x)

        execution_time, _ = measure_execution_time(run_test)
        validate_performance_threshold(execution_time, 1.0, "错误处理性能测试")
