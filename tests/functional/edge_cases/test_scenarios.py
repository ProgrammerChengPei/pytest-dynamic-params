"""
测试边界情况
对应需求文档中的边界情况测试示例
"""

import pytest

from dynamic_params import param_generator, with_dynamic_params


@param_generator
def edge_case_result(value):
    """处理边界情况的生成器"""
    if value is None:
        return "none_value"
    elif value == "":
        return "empty_string"
    elif value < 0:
        return "negative_value"
    else:
        return f"normal_{value}"


@param_generator
def exception_result(value):
    """处理异常输入的生成器"""
    try:
        return 10 / value
    except ZeroDivisionError:
        return "division_by_zero"


class TestEdgeCases:
    """测试边界情况的测试类"""

    @with_dynamic_params(edge_result=edge_case_result)
    @pytest.mark.parametrize("value", [None, "", -1, 0, 1, 1000000])
    def test_edge_cases(self, value, edge_result):
        """测试边界情况"""
        if value is None:
            assert edge_result == "none_value"
        elif value == "":
            assert edge_result == "empty_string"
        elif value < 0:
            assert edge_result == "negative_value"
        else:
            assert edge_result == f"normal_{value}"

    @with_dynamic_params(exception_result=exception_result)
    @pytest.mark.parametrize("value", [1, 2, 0, 5])
    def test_exception_handling(self, value, exception_result):
        """测试异常输入处理"""
        if value == 0:
            assert exception_result == "division_by_zero"
        else:
            assert exception_result == 10 / value
