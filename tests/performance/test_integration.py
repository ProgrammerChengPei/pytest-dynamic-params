"""
集成性能测试 - 测试与pytest的集成性能
"""

import pytest

from dynamic_params import dynamic_params, param_generator
from tests.utils import measure_execution_time, validate_performance_threshold


class TestIntegrationPerformance:
    """集成性能测试类"""

    def test_pytest_parametrize_integration(self):
        """测试与pytest.mark.parametrize的集成性能"""

        @param_generator
        def generate_value(x):
            return x * 2

        @dynamic_params(doubled=generate_value)
        @pytest.mark.parametrize("x", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        def test_func(x, doubled):
            assert doubled == x * 2

        def run_test():
            for x in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
                test_func(x, x * 2)

        execution_time, _ = measure_execution_time(run_test)
        validate_performance_threshold(execution_time, 1.0, "pytest参数化集成测试")

    def test_nested_fixtures_integration(self):
        """测试与嵌套fixtures的集成性能"""

        @param_generator
        def generate_base(x):
            return x + 5

        @param_generator
        def generate_derived(base):
            return base * 3

        @dynamic_params(base=generate_base, derived=generate_derived)
        def test_func(x, base, derived):
            assert base == x + 5
            assert derived == (x + 5) * 3

        def run_test():
            for x in range(20):
                test_func(x, x + 5, (x + 5) * 3)

        execution_time, _ = measure_execution_time(run_test)
        validate_performance_threshold(execution_time, 1.0, "嵌套fixtures集成测试")

    def test_large_test_suite_integration(self):
        """测试大型测试套件的集成性能"""
        # 创建多个生成器
        generators = {}
        for i in range(5):

            def create_generator(j):
                @param_generator
                def gen(x):
                    return x + j

                return gen

            generators[f"value_{i}"] = create_generator(i)

        @dynamic_params(**generators)
        def test_func(x, **kwargs):
            for i in range(5):
                assert kwargs[f"value_{i}"] == x + i

        def run_test():
            for x in range(30):
                expected = {f"value_{i}": x + i for i in range(5)}
                test_func(x, **expected)

        execution_time, _ = measure_execution_time(run_test)
        validate_performance_threshold(execution_time, 1.0, "大型测试套件集成测试")
