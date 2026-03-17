import functools
from typing import Callable, Dict, Any

import pytest


class DynRef:
    """
    动态引用类，用于在 dynamic_parametrize 中直接引用参数和 fixture
    """

    def __init__(self, name: str, ref_type: str = "param"):
        """
        初始化动态引用

        Args:
            name: 引用的名称（参数名或 fixture 名）
            ref_type: 引用类型，'param' 或 'fixture'
        """
        self.name = name
        self.ref_type = ref_type

    def resolve(self, context: Dict[str, Any], request) -> Any:
        """
        解析引用，从上下文或 request 中获取值

        Args:
            context: 上下文字典，包含已解析的参数值
            request: pytest 的 request 对象，用于获取 fixture 值

        Returns:
            解析后的值
        """
        if self.name in context:
            return context[self.name]
        elif self.ref_type == "fixture" and hasattr(request, "getfixturevalue"):
            return request.getfixturevalue(self.name)
        else:
            raise ValueError(f"无法解析引用: {self.name}")


class _ParamGeneratorDecorator:
    """
    参数生成器装饰器类
    """

    def __init__(self, scope: str = "function", cache: bool = True, lazy: bool = True):
        self.scope = scope
        self.cache_enabled = cache
        self.lazy_support = lazy

    def __call__(self, func: Callable) -> Callable:
        """
        装饰器调用入口
        """
        # 添加类型标记（供dynamic_params验证）
        func._is_param_generator = True  # type: ignore[attr-defined]
        func._scope = self.scope  # type: ignore[attr-defined]
        func._cache_enabled = self.cache_enabled  # type: ignore[attr-defined]
        func._lazy_support = self.lazy_support  # type: ignore[attr-defined]
        func._decorator_args = {  # type: ignore[attr-defined]
            "scope": self.scope,
            "cache_enabled": self.cache_enabled,
            "lazy_support": self.lazy_support,
        }

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper


def param_generator(
    func_or_scope=None, scope: str = "function", cache: bool = True, lazy: bool = True
):
    """
    参数生成器装饰器，支持两种用法:
    1. @param_generator (无参数)
    2. @param_generator(scope="session") (有参数)
    """
    # 如果第一个参数是可调用的，说明是 @param_generator 用法
    if callable(func_or_scope):
        # 直接装饰函数
        decorator = _ParamGeneratorDecorator(scope=scope, cache=cache, lazy=lazy)
        return decorator(func_or_scope)
    else:
        # 是 @param_generator() 或 @param_generator(scope="...") 用法
        # 返回配置好的装饰器实例
        actual_scope = func_or_scope if func_or_scope is not None else scope
        return _ParamGeneratorDecorator(scope=actual_scope, cache=cache, lazy=lazy)


def use_generators(**param_mapping: Callable):
    """使用动态参数装饰器，将参数生成器与测试函数关联起来"""

    def decorator(test_func: Callable) -> Callable:
        # Validate param_mapping
        for param_name, generator_func in param_mapping.items():
            if not callable(generator_func):
                raise ValueError(
                    f"Generator for parameter '{param_name}' must be callable"
                )

            # Verify generator is properly decorated
            if not hasattr(generator_func, "_is_param_generator"):
                func_name = getattr(generator_func, "__name__", str(generator_func))
                raise ValueError(
                    f"Function {func_name} must be decorated " f"with @param_generator"
                )

        # Initialize dynamic param attributes on test function
        test_func._mapping = param_mapping  # type: ignore[attr-defined]
        test_func._requires = True  # type: ignore[attr-defined]

        # Mark function as dynamic param test
        test_func.pytestmark = getattr(test_func, "pytestmark", [])  # type: ignore
        test_func.pytestmark.append(pytest.mark.dynamic_param)  # type: ignore

        @functools.wraps(test_func)
        def wrapper(*args, **kwargs):
            return test_func(*args, **kwargs)

        # 传递动态参数元数据到wrapper
        wrapper._mapping = test_func._mapping  # type: ignore[attr-defined]
        wrapper._requires = test_func._requires  # type: ignore[attr-defined]

        # 确保wrapper也被识别为测试
        wrapper.pytestmark = getattr(wrapper, "pytestmark", [])  # type: ignore
        wrapper.pytestmark.append(pytest.mark.dynamic_param)  # type: ignore

        # 确保wrapper有正确的 __name__
        wrapper.__name__ = test_func.__name__

        return wrapper

    return decorator


def dynamic_parametrize(*param_args, **param_kwargs):
    """
    动态参数化装饰器，替代 pytest.mark.parametrize
    支持在参数化中使用 DynRef 引用其他参数和 fixture

    Args:
        *param_args: 与 pytest.mark.parametrize 相同的参数格式
        **param_kwargs: 与 pytest.mark.parametrize 相同的关键字参数
    """

    def decorator(test_func: Callable) -> Callable:
        # 存储参数化信息
        if not hasattr(test_func, "_dynamic_parametrize"):
            test_func._dynamic_parametrize = []  # type: ignore[attr-defined]

        test_func._dynamic_parametrize.append(
            {"args": param_args, "kwargs": param_kwargs}  # type: ignore[attr-defined]
        )

        # 标记测试函数需要动态参数化
        test_func._requires_dynamic_parametrize = True  # type: ignore[attr-defined]

        # Mark function as dynamic parametrize test
        test_func.pytestmark = getattr(test_func, "pytestmark", [])  # type: ignore
        test_func.pytestmark.append(pytest.mark.dynamic_parametrize)  # type: ignore

        @functools.wraps(test_func)
        def wrapper(*args, **kwargs):
            return test_func(*args, **kwargs)

        # 传递动态参数化元数据到wrapper
        wrapper._dynamic_parametrize = (
            test_func._dynamic_parametrize  # type: ignore[attr-defined]
        )
        wrapper._requires_dynamic_parametrize = (
            test_func._requires_dynamic_parametrize  # type: ignore[attr-defined]
        )

        # 确保wrapper也被识别为测试
        wrapper.pytestmark = getattr(wrapper, "pytestmark", [])  # type: ignore
        wrapper.pytestmark.append(pytest.mark.dynamic_parametrize)  # type: ignore

        # 确保wrapper有正确的 __name__
        wrapper.__name__ = test_func.__name__

        return wrapper

    return decorator
