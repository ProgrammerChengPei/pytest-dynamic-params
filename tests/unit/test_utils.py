"""工具函数模块的单元测试"""

from src.dynamic_params.utils import (
    get_function_signature,
    normalize_param_value,
    validate_param_name,
)


class TestGetFunctionSignature:
    """get_function_signature函数的测试类"""
    
    def test_get_function_signature(self):
        """测试获取函数签名"""
        def sample_func(a, b, c=10):
            return a + b + c
        
        signature = get_function_signature(sample_func)
        
        assert "sample_func" in signature
        assert "(a, b, c=10)" in signature

    def test_get_function_signature_no_params(self):
        """测试无参函数的签名"""
        def no_param_func():
            return "no params"
        
        signature = get_function_signature(no_param_func)
        
        assert "no_param_func" in signature
        assert "()" in signature


class TestValidateParamName:
    """validate_param_name函数的测试类"""
    
    def test_valid(self):
        """测试有效的参数名称"""
        assert validate_param_name("valid_name") is True
        assert validate_param_name("name123") is True
        assert validate_param_name("_private") is True
        assert validate_param_name("mixed_Case_Name") is True

    def test_invalid(self):
        """测试无效的参数名称"""
        assert validate_param_name("") is False
        assert validate_param_name("123invalid") is False  # 不能以数字开头
        assert validate_param_name("name with spaces") is False  # 不能包含空格
        assert validate_param_name("name-invalid") is False  # 不能包含连字符
        assert validate_param_name("name.invalid") is False  # 不能包含点号

    def test_none_or_non_string(self):
        """测试None或非字符串参数"""
        assert validate_param_name(None) is False
        assert validate_param_name(123) is False
        assert validate_param_name([]) is False
        assert validate_param_name({}) is False


class TestNormalizeParamValue:
    """normalize_param_value函数的测试类"""
    
    def test_normalize_param_value(self):
        """测试参数值标准化"""
        # normalize_param_value函数目前只是返回原始值
        assert normalize_param_value("test") == "test"
        assert normalize_param_value(123) == 123
        assert normalize_param_value([1, 2, 3]) == [1, 2, 3]
        assert normalize_param_value({"key": "value"}) == {"key": "value"}
        assert normalize_param_value(None) is None

    def test_normalize_param_value_special_cases(self):
        """测试参数值标准化的特殊情况"""
        assert normalize_param_value(True) is True
        assert normalize_param_value(False) is False
        assert normalize_param_value(0) == 0
        assert normalize_param_value("") == ""