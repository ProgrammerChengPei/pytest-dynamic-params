"""
测试嵌套关系的单元测试
对应 specs/需求.md 第230-502行的嵌套关系示例
"""

import pytest
from dynamic_params import dynamic_params, param_generator
from dynamic_params.core.generator import ParamGenerator
from dynamic_params.core.registry import GeneratorRegistry


# 测试参数生成器基本功能
def test_param_generator_basic():
    """测试参数生成器的基本功能"""
    @param_generator
    def simple_generator():
        return "test"

    # 测试生成器属性
    assert hasattr(simple_generator, "_is_param_generator")
    assert simple_generator._is_param_generator is True
    assert hasattr(simple_generator, "_scope")
    assert simple_generator._scope == "function"


# 测试参数生成器依赖解析
def test_param_generator_dependency_extraction():
    """测试参数生成器的依赖提取"""
    @param_generator
    def dependent_generator(a, b, c):
        return a + b + c

    # 创建参数生成器实例
    registry = GeneratorRegistry.get_instance()
    generator = registry.register(dependent_generator, "test_param")

    # 测试依赖提取
    assert "a" in generator.dependencies
    assert "b" in generator.dependencies
    assert "c" in generator.dependencies
    assert len(generator.dependencies) == 3


# 测试动态参数调用静态参数
def test_dynamic_param_calls_static_param():
    """测试动态参数调用静态参数"""
    @param_generator
    def multiply_by_two(value):
        return value * 2

    # 模拟测试函数
    @dynamic_params(result=multiply_by_two)
    def test_func(value, result):
        assert result == value * 2

    # 验证动态参数映射
    assert hasattr(test_func, "_mapping")
    assert "result" in test_func._mapping


# 测试动态参数调用动态参数
def test_dynamic_param_calls_dynamic_param():
    """测试动态参数调用动态参数"""
    @param_generator
    def add_one(value):
        return value + 1

    @param_generator
    def add_two(add_one_result):
        return add_one_result + 1

    # 模拟测试函数
    @dynamic_params(result1=add_one, result2=add_two)
    def test_func(value, result1, result2):
        assert result1 == value + 1
        assert result2 == value + 2

    # 验证动态参数映射
    assert hasattr(test_func, "_mapping")
    assert "result1" in test_func._mapping
    assert "result2" in test_func._mapping


# 测试参数生成器缓存
def test_param_generator_cache():
    """测试参数生成器的缓存功能"""
    call_count = 0

    @param_generator(cache=True)
    def cached_generator(value):
        nonlocal call_count
        call_count += 1
        return value * 2

    # 创建参数生成器实例
    registry = GeneratorRegistry.get_instance()
    generator = registry.register(cached_generator, "cached_param")

    # 第一次调用
    context1 = {"value": 5}
    result1 = generator.get_result(context1)
    assert result1 == 10
    assert call_count == 1

    # 第二次调用（应该使用缓存）
    result2 = generator.get_result(context1)
    assert result2 == 10
    assert call_count == 1  # 调用次数应该不变


# 测试参数生成器作用域
def test_param_generator_scope():
    """测试参数生成器的作用域设置"""
    @param_generator(scope="session")
    def session_generator():
        return "session_value"

    # 测试作用域属性
    assert hasattr(session_generator, "_scope")
    assert session_generator._scope == "session"


# 测试参数生成器懒加载
def test_param_generator_lazy():
    """测试参数生成器的懒加载功能"""
    @param_generator(lazy=True)
    def lazy_generator():
        return "lazy_value"

    # 测试懒加载属性
    assert hasattr(lazy_generator, "_lazy_support")
    assert lazy_generator._lazy_support is True


# 测试缺失参数错误处理
def test_param_generator_missing_param():
    """测试参数生成器处理缺失参数的情况"""
    @param_generator
    def dependent_generator(a, b):
        return a + b

    # 创建参数生成器实例
    registry = GeneratorRegistry.get_instance()
    generator = registry.register(dependent_generator, "test_param")

    # 测试缺失参数
    context = {"a": 1}  # 缺少 b
    from dynamic_params.errors import MissingParameterError
    with pytest.raises(MissingParameterError):
        generator.get_result(context)


# 测试参数生成器执行错误处理
def test_param_generator_execution_error():
    """测试参数生成器执行错误的情况"""
    @param_generator
    def error_generator():
        raise ValueError("Test error")

    # 创建参数生成器实例
    registry = GeneratorRegistry.get_instance()
    generator = registry.register(error_generator, "error_param")

    # 测试执行错误
    context = {}
    with pytest.raises(ValueError):
        generator.get_result(context)


# 测试参数生成器结果类型
def test_param_generator_result_types():
    """测试参数生成器返回不同类型的结果"""
    # 测试返回字符串
    @param_generator
    def string_generator():
        return "string"

    # 测试返回数字
    @param_generator
    def number_generator():
        return 42

    # 测试返回列表
    @param_generator
    def list_generator():
        return [1, 2, 3]

    # 测试返回字典
    @param_generator
    def dict_generator():
        return {"key": "value"}

    # 创建参数生成器实例
    registry = GeneratorRegistry.get_instance()
    string_gen = registry.register(string_generator, "string_param")
    number_gen = registry.register(number_generator, "number_param")
    list_gen = registry.register(list_generator, "list_param")
    dict_gen = registry.register(dict_generator, "dict_param")

    # 测试结果类型
    assert isinstance(string_gen.get_result({}), str)
    assert isinstance(number_gen.get_result({}), int)
    assert isinstance(list_gen.get_result({}), list)
    assert isinstance(dict_gen.get_result({}), dict)


# 测试参数生成器依赖链
def test_param_generator_dependency_chain():
    """测试参数生成器的依赖链"""
    @param_generator
    def level1():
        return 1

    @param_generator
    def level2(level1):
        return level1 + 1

    @param_generator
    def level3(level2):
        return level2 + 1

    # 创建参数生成器实例
    registry = GeneratorRegistry.get_instance()
    gen1 = registry.register(level1, "level1")
    gen2 = registry.register(level2, "level2")
    gen3 = registry.register(level3, "level3")

    # 测试依赖链
    context = {}
    result1 = gen1.get_result(context)
    context["level1"] = result1
    result2 = gen2.get_result(context)
    context["level2"] = result2
    result3 = gen3.get_result(context)

    assert result1 == 1
    assert result2 == 2
    assert result3 == 3
