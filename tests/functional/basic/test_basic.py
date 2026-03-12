"""
示例1: 基础用法（无fixture）
对应 specs/需求.md 第303-311行的使用示例
"""

import pytest

from dynamic_params import dynamic_params
from tests.generators.basic import calculate_result


class TestBasic:
    """测试基础用法的测试类"""

    @dynamic_params(result=calculate_result)
    @pytest.mark.parametrize("input_value", [1, 2, 3])
    def test_basic(self, input_value, result):
        """测试用例数量：3个"""
        assert result == input_value * 2

    @dynamic_params(result=calculate_result)
    @pytest.mark.parametrize("input_value", [0, -1, 1000])
    def test_basic_edge_cases(self, input_value, result):
        """测试边界情况：0、负数、大数"""
        assert result == input_value * 2

    @dynamic_params(result=calculate_result)
    @pytest.mark.parametrize("input_value", [1.5, 2.7, 3.9])
    def test_basic_float_values(self, input_value, result):
        """测试浮点数输入"""
        assert result == input_value * 2
