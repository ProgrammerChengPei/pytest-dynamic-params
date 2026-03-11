import functools
from typing import Callable

import pytest


class _ParamGeneratorDecorator:
    """
    参数生成器装饰器类
    """

    def __init__(
        self, scope: str = "function", cache: bool = True, lazy: bool = True
    ):
        self.scope = scope
        self.cache_enabled = cache
        self.lazy_support = lazy

    def __call__(self, func: Callable) -> Callable:
        """
        装饰器调用入口
        """
        # 添加类型标记（供with_dynamic_params验证）
        func._is_param_generator = True
        func._scope = self.scope
        func._cache_enabled = self.cache_enabled
        func._lazy_support = self.lazy_support
        func._decorator_args = {
            "scope": self.scope,
            "cache_enabled": self.cache_enabled,
            "lazy_support": self.lazy_support,
        }

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper


def param_generator(
    func_or_scope=None,
    scope: str = "function",
    cache: bool = True,
    lazy: bool = True
):
    """
    参数生成器装饰器，支持两种用法:
    1. @param_generator (无参数)
    2. @param_generator(scope="session") (有参数)
    """
    # 如果第一个参数是可调用的，说明是 @param_generator 用法
    if callable(func_or_scope):
        # 直接装饰函数
        decorator = _ParamGeneratorDecorator(
            scope=scope, cache=cache, lazy=lazy
        )
        return decorator(func_or_scope)
    else:
        # 是 @param_generator() 或 @param_generator(scope="...") 用法
        # 返回配置好的装饰器实例
        actual_scope = func_or_scope if func_or_scope is not None else scope
        return _ParamGeneratorDecorator(
            scope=actual_scope, cache=cache, lazy=lazy
        )


def with_dynamic_params(**param_mapping: Callable):
    def decorator(test_func: Callable) -> Callable:
        # Validate param_mapping
        for param_name, generator_func in param_mapping.items():
            if not callable(generator_func):
                raise ValueError(
                    f"Generator for parameter '{param_name}' must be callable"
                )

            # Verify generator is properly decorated
            if not hasattr(generator_func, "_is_param_generator"):
                func_name = getattr(
                    generator_func, "__name__", str(generator_func)
                )
                raise ValueError(
                    f"Function {func_name} must be decorated "
                    f"with @param_generator"
                )

        # Initialize dynamic param attributes on test function
        test_func._dynamic_param_mapping = param_mapping
        test_func._requires_dynamic_params = True

        # Mark function as dynamic param test
        test_func.pytestmark = getattr(test_func, "pytestmark", [])
        test_func.pytestmark.append(
            pytest.mark.dynamic_param
        )

        @functools.wraps(test_func)
        def wrapper(*args, **kwargs):
            return test_func(*args, **kwargs)

        # 传递动态参数元数据到wrapper
        wrapper._dynamic_param_mapping = test_func._dynamic_param_mapping
        wrapper._requires_dynamic_params = test_func._requires_dynamic_params

        # 确保wrapper也被识别为测试
        wrapper.pytestmark = getattr(wrapper, "pytestmark", [])
        wrapper.pytestmark.append(pytest.mark.dynamic_param)

        # 确保wrapper有正确的 __name__
        wrapper.__name__ = test_func.__name__

        return wrapper

    return decorator
