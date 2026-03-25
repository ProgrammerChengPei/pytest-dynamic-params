import functools
from typing import Callable

from ...plugin.processors import process_use_generators


def use_generators(**generator_mapping: Callable):
    """使用动态参数装饰器，将参数生成器与函数关联起来"""

    def decorator(func: Callable) -> Callable:
        # 使用处理器处理装饰器逻辑
        processed_func = process_use_generators(func, generator_mapping)

        @functools.wraps(processed_func)
        def wrapper(*args, **kwargs):
            return processed_func(*args, **kwargs)

        # 传递动态参数元数据到wrapper
        wrapper._mapping = processed_func._mapping  # type: ignore
        wrapper._is_mapped = processed_func._is_mapped  # type: ignore

        # 确保wrapper也被标记
        wrapper.pytestmark = getattr(
            processed_func,
            "pytestmark",
            []
        )  # type: ignore

        # 确保wrapper有正确的 __name__
        wrapper.__name__ = processed_func.__name__

        return wrapper

    return decorator
