"""
测试参数生成器与静态参数的依赖关系
对应需求文档中关于依赖解析的部分
"""

import pytest

from dynamic_params import dynamic_params, param_generator


# 创建依赖于静态参数的生成器
@param_generator
def complex_calculation(seed_value, multiplier, offset):
    """依赖于多个静态参数的复杂计算"""
    return {
        "result": seed_value * multiplier + offset,
        "details": (
            f"{seed_value} * {multiplier} + {offset} = "
            f"{seed_value * multiplier + offset}"
        ),
    }


class TestGeneratorParamDependencies:
    """测试参数生成器对静态参数依赖关系的测试类"""

    @dynamic_params(calc=complex_calculation)
    @pytest.mark.parametrize("seed_value", [1, 2])
    @pytest.mark.parametrize("multiplier", [10, 20])
    @pytest.mark.parametrize("offset", [5, 15])
    def test_generator_param_dependencies(self, seed_value, multiplier, offset, calc):
        """测试参数生成器对静态参数的依赖：
        seed_value/multiplier/offset → complex_calculation
        """
        expected_result = seed_value * multiplier + offset

        # 验证计算结果
        assert calc["result"] == expected_result
        assert str(expected_result) in calc["details"]
        assert str(seed_value) in calc["details"]
        assert str(multiplier) in calc["details"]
        assert str(offset) in calc["details"]
