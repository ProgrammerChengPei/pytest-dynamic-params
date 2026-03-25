"""
测试 dynamic_parametrize 装饰器的单元测试
"""

import pytest

from dynamic_params import dynamic_parametrize, DynRef


# 测试 DynRef 类
def test_dynref_initialization():
    """测试 DynRef 类的初始化"""
    # 测试默认 ref_type
    ref1 = DynRef("param1")
    assert ref1.name == "param1"
    assert ref1.ref_type == "param"
    
    # 测试指定 ref_type
    ref2 = DynRef("fixture1", ref_type="fixture")
    assert ref2.name == "fixture1"
    assert ref2.ref_type == "fixture"


def test_dynref_resolve_from_context():
    """测试从上下文中解析 DynRef"""
    ref = DynRef("param1")
    context = {"param1": "value1"}
    
    # 模拟 request 对象
    class MockRequest:
        pass
    
    request = MockRequest()
    result = ref.resolve(context, request)
    assert result == "value1"


def test_dynref_resolve_from_fixture():
    """测试从 fixture 中解析 DynRef"""
    ref = DynRef("fixture1", ref_type="fixture")
    context = {}
    
    # 模拟 request 对象
    class MockRequest:
        def getfixturevalue(self, name):
            if name == "fixture1":
                return "fixture_value"
            raise ValueError(f"Fixture {name} not found")
    
    request = MockRequest()
    result = ref.resolve(context, request)
    assert result == "fixture_value"


def test_dynref_resolve_not_found():
    """测试解析不存在的引用"""
    ref = DynRef("non_existent")
    context = {}
    
    # 模拟 request 对象
    class MockRequest:
        pass
    
    request = MockRequest()
    
    with pytest.raises(ValueError, match="无法解析引用: non_existent"):
        ref.resolve(context, request)


# 测试 dynamic_parametrize 装饰器
def test_dynamic_parametrize_basic():
    """测试 dynamic_parametrize 装饰器的基本功能"""
    
    @dynamic_parametrize("param", [1, 2, 3])
    def test_func(param):
        assert isinstance(param, int)
    
    # 验证装饰器添加的属性
    assert hasattr(test_func, "_is_parametrized")
    assert test_func._is_parametrized is True
    assert hasattr(test_func, "_parametrize_info")
    assert len(test_func._parametrize_info) == 1


def test_dynamic_parametrize_with_dynref():
    """测试 dynamic_parametrize 装饰器使用 DynRef"""
    
    @dynamic_parametrize("param1", [1, 2])
    @dynamic_parametrize("param2", [DynRef("param1")])
    def test_func(param1, param2):
        assert param2 == param1
    
    # 验证装饰器添加的属性
    assert hasattr(test_func, "_is_parametrized")
    assert test_func._is_parametrized is True
    assert hasattr(test_func, "_parametrize_info")
    assert len(test_func._parametrize_info) == 2


def test_dynamic_parametrize_with_kwargs():
    """测试 dynamic_parametrize 装饰器使用关键字参数"""
    
    @dynamic_parametrize("param", [1, 2, 3], ids=["one", "two", "three"])
    def test_func(param):
        assert isinstance(param, int)
    
    # 验证装饰器添加的属性
    assert hasattr(test_func, "_is_parametrized")
    assert test_func._is_parametrized is True
    assert hasattr(test_func, "_parametrize_info")
    assert len(test_func._parametrize_info) == 1
    assert "ids" in test_func._parametrize_info[0]["kwargs"]


def test_dynref_resolve_with_fixture_not_available():
    """测试 DynRef 解析 fixture 但 fixture 不可用的情况"""
    ref = DynRef("fixture1", ref_type="fixture")
    context = {}
    
    # 模拟没有 getfixturevalue 方法的 request 对象
    class MockRequest:
        pass
    
    request = MockRequest()
    
    with pytest.raises(ValueError, match="无法解析引用: fixture1"):
        ref.resolve(context, request)


def test_dynamic_parametrize_wrapper_calls_original():
    """测试 dynamic_parametrize 装饰器的包装函数调用原始函数"""
    call_count = 0
    
    @dynamic_parametrize("param", [1])
    def test_func(param):
        nonlocal call_count
        call_count += 1
        return param
    
    # 调用包装函数
    result = test_func(1)
    assert result == 1
    assert call_count == 1


def test_dynamic_parametrize_preserves_function_name():
    """测试 dynamic_parametrize 装饰器保留函数名称"""
    
    @dynamic_parametrize("param", [1])
    def custom_test_function(param):
        pass
    
    assert custom_test_function.__name__ == "custom_test_function"


def test_dynamic_parametrize_with_empty_args():
    """测试 dynamic_parametrize 装饰器使用空参数"""
    
    @dynamic_parametrize()
    def test_func():
        pass
    
    # 验证装饰器添加的属性
    assert hasattr(test_func, "_is_parametrized")
    assert test_func._is_parametrized is True
    assert hasattr(test_func, "_parametrize_info")
    assert len(test_func._parametrize_info) == 1
