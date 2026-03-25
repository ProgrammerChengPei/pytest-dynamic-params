"""
测试 use_generators 装饰器处理器的单元测试
"""

import pytest

from dynamic_params import generator
from dynamic_params.errors import InvalidGeneratorError
from dynamic_params.plugin.processors.use_generators import process_use_generators


class TestUseGeneratorsProcessor:
    """process_use_generators 函数的测试类"""

    def test_process_use_generators(self):
        """测试处理 @use_generators 装饰器"""
        # 定义一个测试函数
        def test_func(result):
            pass
        
        # 定义一个生成器函数
        @generator
        def test_generator():
            return 42
        
        # 调用处理器
        mapping = {"result": test_generator}
        processed_func = process_use_generators(test_func, mapping)
        
        # 验证处理器添加的属性
        assert hasattr(processed_func, "_is_mapped")
        assert processed_func._is_mapped is True
        assert hasattr(processed_func, "_mapping")
        assert processed_func._mapping == mapping
        assert hasattr(processed_func, "pytestmark")
        assert len(processed_func.pytestmark) > 0

    def test_process_use_generators_with_invalid_generator(self):
        """测试处理 @use_generators 装饰器时，使用无效的生成器"""
        # 定义一个测试函数
        def test_func(result):
            pass
        
        # 定义一个普通函数（不是生成器）
        def not_a_generator():
            return 42
        
        # 调用处理器，应该抛出 InvalidGeneratorError
        mapping = {"result": not_a_generator}
        with pytest.raises(InvalidGeneratorError):
            process_use_generators(test_func, mapping)

    def test_process_use_generators_with_non_callable(self):
        """测试处理 @use_generators 装饰器时，使用非可调用对象"""
        # 定义一个测试函数
        def test_func(result):
            pass
        
        # 调用处理器，应该抛出 ValueError
        mapping = {"result": 42}  # 非可调用对象
        with pytest.raises(ValueError):
            process_use_generators(test_func, mapping)

    def test_process_use_generators_with_wrapped_generator(self):
        """测试处理 @use_generators 装饰器时，使用包装后的生成器"""
        # 定义一个测试函数
        def test_func(result):
            pass
        
        # 定义一个生成器函数
        @generator
        def test_generator():
            return 42
        
        # 包装生成器函数
        def wrapper(func):
            def inner(*args, **kwargs):
                return func(*args, **kwargs)
            inner.__wrapped__ = func
            return inner
        
        wrapped_generator = wrapper(test_generator)
        
        # 调用处理器
        mapping = {"result": wrapped_generator}
        processed_func = process_use_generators(test_func, mapping)
        
        # 验证处理器添加的属性
        assert hasattr(processed_func, "_is_mapped")
        assert processed_func._is_mapped is True
        assert hasattr(processed_func, "_mapping")
        assert processed_func._mapping == mapping
        assert hasattr(processed_func, "pytestmark")
        assert len(processed_func.pytestmark) > 0
