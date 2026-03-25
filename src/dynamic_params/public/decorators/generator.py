import functools
from typing import Callable


class _GeneratorDecorator:
    """
    生成器装饰器类
    """

    def __init__(
        self,
        scope: str = "function",
        cache: bool = True,
        lazy: bool = True
    ):
        self.scope = scope
        self.cache_enabled = cache
        self.lazy_support = lazy

    def __call__(self, func: Callable) -> Callable:
        """
        装饰器调用入口
        """
        # 添加类型标记（供dynamic_params验证）
        func._is_generator = True  # type: ignore[attr-defined]
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


def generator(
    func=None, scope: str = "function", cache: bool = True, lazy: bool = True
):
    """
    生成器装饰器，支持两种用法:
    1. @generator (无参数)
    2. @generator(scope="session") (有参数)
    """
    # 如果第一个参数是可调用的，说明是 @generator 用法
    if callable(func):
        # 直接装饰函数
        decorator = _GeneratorDecorator(scope=scope, cache=cache, lazy=lazy)
        return decorator(func)
    else:
        # 是 @generator() 或 @generator(scope="...") 用法
        # 返回配置好的装饰器实例
        return _GeneratorDecorator(scope=scope, cache=cache, lazy=lazy)
