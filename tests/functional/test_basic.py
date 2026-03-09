"""
示例1: 基础用法（无fixture）
对应 specs/需求.md 第303-311行的使用示例
"""
import pytest

from dynamic_params import with_dynamic_params
from tests.generators.basic import calculate_result


class TestBasic:
    """测试基础用法的测试类"""
    
    @with_dynamic_params(result=calculate_result)
    @pytest.mark.parametrize("input_value", [1, 2, 3])
    def test_basic(self, input_value, result):
        """测试用例数量：3个"""
        assert result == input_value * 2