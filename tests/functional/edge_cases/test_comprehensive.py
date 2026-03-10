"""
综合边界情况测试
测试各种边界值和异常输入场景
"""
import pytest
from dynamic_params import param_generator, with_dynamic_params


@param_generator
def handle_edge_cases(value):
    """处理边界情况的生成器"""
    if value is None:
        return "none_value"
    elif value == "":
        return "empty_string"
    elif isinstance(value, (int, float)):
        if value < 0:
            return "negative_value"
        elif value == 0:
            return "zero_value"
        elif value > 1000000:
            return "large_value"
        else:
            return f"normal_{value}"
    else:
        return f"normal_{value}"


@param_generator
def handle_exception_input(value):
    """处理异常输入的生成器"""
    try:
        return 10 / value
    except ZeroDivisionError:
        return "division_by_zero"
    except TypeError:
        return "type_error"


@param_generator
def handle_complex_input(data):
    """处理复杂输入的生成器"""
    if not data:
        return "empty_data"
    elif isinstance(data, list):
        return f"list_with_{len(data)}_items"
    elif isinstance(data, dict):
        return f"dict_with_{len(data)}_keys"
    else:
        return f"type_{type(data).__name__}"


class TestEdgeCasesComprehensive:
    """综合边界情况测试类"""
    
    @with_dynamic_params(result=handle_edge_cases)
    @pytest.mark.parametrize("value", [
        None, "", -1, -1000, 0, 1, 1000000, 1000001,  # 基本边界值
        True, False, [], {}, "test", 3.14,  # 不同类型
    ])
    def test_basic_edge_cases(self, value, result):
        """测试基本边界情况"""
        if value is None:
            assert result == "none_value"
        elif value == "":
            assert result == "empty_string"
        elif isinstance(value, (int, float)):
            if value < 0:
                assert result == "negative_value"
            elif value == 0:
                assert result == "zero_value"
            elif value > 1000000:
                assert result == "large_value"
            else:
                assert result == f"normal_{value}"
        else:
            assert result == f"normal_{value}"
    
    @with_dynamic_params(exception_result=handle_exception_input)
    @pytest.mark.parametrize("value", [
        1, 2, 0, 5,  # 数值
        "string", [], {}, None,  # 非数值类型
    ])
    def test_exception_handling(self, value, exception_result):
        """测试异常输入处理"""
        if value == 0:
            assert exception_result == "division_by_zero"
        elif not isinstance(value, (int, float)):
            assert exception_result == "type_error"
        else:
            assert exception_result == 10 / value
    
    @with_dynamic_params(result=handle_complex_input)
    @pytest.mark.parametrize("data", [
        [], [1, 2, 3], {}, {"a": 1, "b": 2},  # 空和非空集合
        "", "test", 123, 3.14, True, None,  # 其他类型
    ])
    def test_complex_inputs(self, data, result):
        """测试复杂输入处理"""
        if not data:
            assert result == "empty_data"
        elif isinstance(data, list):
            assert result == f"list_with_{len(data)}_items"
        elif isinstance(data, dict):
            assert result == f"dict_with_{len(data)}_keys"
        else:
            assert result == f"type_{type(data).__name__}"
    
    @with_dynamic_params(result=handle_edge_cases)
    @pytest.mark.parametrize("value", [
        float('inf'), float('-inf'), float('nan'),  # 特殊浮点数
        " ", "\n", "\t",  # 空白字符串
        999999, 1000000, 1000001,  # 接近边界的整数
    ])
    def test_special_edge_cases(self, value, result):
        """测试特殊边界情况"""
        if value is None:
            assert result == "none_value"
        elif value == "":
            assert result == "empty_string"
        elif isinstance(value, (int, float)):
            if value < 0:
                assert result == "negative_value"
            elif value == 0:
                assert result == "zero_value"
            elif value > 1000000:
                assert result == "large_value"
            else:
                assert result == f"normal_{value}"
        else:
            assert result == f"normal_{value}"