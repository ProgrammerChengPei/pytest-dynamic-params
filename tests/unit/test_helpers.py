"""
测试辅助函数的单元测试
"""

import pytest

from dynamic_params import generator
from dynamic_params.utils.helpers import (
    validate_generator_function,
    get_function_signature,
    extract_function_name,
    is_valid_scope,
    normalize_scope,
    create_cache_key,
    normalize_param_value,
    validate_param_name
)


# 测试 validate_generator_function 函数
def test_validate_generator_function_with_generator():
    """测试验证生成器函数"""
    @generator
    def test_generator():
        return 42
    
    assert validate_generator_function(test_generator) is True


def test_validate_generator_function_with_regular_function():
    """测试验证普通函数"""
    def test_function():
        return 42
    
    assert validate_generator_function(test_function) is False


def test_validate_generator_function_with_non_callable():
    """测试验证非可调用对象"""
    assert validate_generator_function(42) is False


def test_validate_generator_function_with_wrapped_generator():
    """测试验证包装后的生成器函数"""
    @generator
    def test_generator():
        return 42
    
    # 模拟包装函数
    def wrapper(func):
        def inner(*args, **kwargs):
            return func(*args, **kwargs)
        inner.__wrapped__ = func
        return inner
    
    wrapped_generator = wrapper(test_generator)
    assert validate_generator_function(wrapped_generator) is True


# 测试 get_function_signature 函数
def test_get_function_signature():
    """测试获取函数签名"""
    def test_function(a, b, c=1):
        return a + b + c
    
    signature = get_function_signature(test_function)
    assert len(signature.parameters) == 3
    assert "a" in signature.parameters
    assert "b" in signature.parameters
    assert "c" in signature.parameters


def test_get_function_signature_with_wrapped():
    """测试获取包装函数的签名"""
    def test_function(a, b):
        return a + b
    
    # 模拟包装函数
    def wrapper(func):
        def inner(*args, **kwargs):
            return func(*args, **kwargs)
        inner.__wrapped__ = func
        return inner
    
    wrapped_function = wrapper(test_function)
    signature = get_function_signature(wrapped_function)
    assert len(signature.parameters) == 2
    assert "a" in signature.parameters
    assert "b" in signature.parameters


# 测试 extract_function_name 函数
def test_extract_function_name():
    """测试提取函数名称"""
    def test_function():
        return 42
    
    assert extract_function_name(test_function) == "test_function"


def test_extract_function_name_with_wrapped():
    """测试提取包装函数的名称"""
    def test_function():
        return 42
    
    # 模拟包装函数
    def wrapper(func):
        def inner(*args, **kwargs):
            return func(*args, **kwargs)
        inner.__wrapped__ = func
        return inner
    
    wrapped_function = wrapper(test_function)
    assert extract_function_name(wrapped_function) == "test_function"


# 测试 is_valid_scope 函数
def test_is_valid_scope():
    """测试检查作用域是否有效"""
    valid_scopes = ["function", "class", "module", "session"]
    for scope in valid_scopes:
        assert is_valid_scope(scope) is True
    
    invalid_scopes = ["invalid", "global", "local"]
    for scope in invalid_scopes:
        assert is_valid_scope(scope) is False


# 测试 normalize_scope 函数
def test_normalize_scope():
    """测试标准化作用域"""
    valid_scopes = ["function", "class", "module", "session"]
    for scope in valid_scopes:
        assert normalize_scope(scope) == scope
    
    assert normalize_scope("invalid") == "function"


# 测试 create_cache_key 函数
def test_create_cache_key():
    """测试创建缓存键"""
    context = {"a": 1, "b": 2, "c": 3}
    dependencies = ["a", "b"]
    cache_key = create_cache_key(context, dependencies)
    assert isinstance(cache_key, str)
    
    # 测试相同上下文生成相同缓存键
    cache_key2 = create_cache_key(context, dependencies)
    assert cache_key == cache_key2
    
    # 测试不同上下文生成不同缓存键
    context3 = {"a": 1, "b": 3, "c": 3}
    cache_key3 = create_cache_key(context3, dependencies)
    assert cache_key != cache_key3


# 测试 normalize_param_value 函数
def test_normalize_param_value():
    """测试标准化参数值"""
    # 测试字符串
    assert normalize_param_value("  test  ") == "test"
    # 测试数字
    assert normalize_param_value(42) == 42
    # 测试列表
    assert normalize_param_value([1, 2, 3]) == [1, 2, 3]
    # 测试字典
    assert normalize_param_value({"a": 1, "b": 2}) == {"a": 1, "b": 2}


# 测试 validate_param_name 函数
def test_validate_param_name():
    """测试验证参数名是否有效"""
    # 测试有效参数名
    valid_names = ["param", "param1", "param_name"]
    for name in valid_names:
        assert validate_param_name(name) is True
    
    # 测试无效参数名
    invalid_names = ["", 123, "1param", "param-name"]
    for name in invalid_names:
        assert validate_param_name(name) is False
