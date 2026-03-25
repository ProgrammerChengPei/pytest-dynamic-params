"""@use_generators 装饰器处理器"""

from typing import Callable, Dict

import pytest

from ...errors import InvalidGeneratorError


def process_use_generators(
    func: Callable,
    mapping: Dict[str, Callable]
) -> Callable:
    """处理 @use_generators 装饰器

    Args:
        func: 被装饰的函数
        mapping: 参数名到生成器函数的映射

    Returns:
        处理后的函数
    """
    # 验证映射中的所有值都是可调用的
    for param_name, generator_func in mapping.items():
        if not callable(generator_func):
            raise ValueError(f"参数 {param_name} 的值必须是可调用对象")

        # 验证生成器函数是否由 @generator 装饰
        actual_func = generator_func
        while hasattr(actual_func, "__wrapped__"):
            actual_func = actual_func.__wrapped__

        if (not hasattr(actual_func, "_is_generator") or
                    not actual_func._is_generator):
                raise InvalidGeneratorError(
                    "函数 {0} 不是参数生成器，请使用 @generator 装饰".format(generator_func.__name__)
                )

    # 为函数添加标记，以便 pytest_generate_tests 钩子识别
    func._is_mapped = True  # type: ignore
    func._mapping = mapping  # type: ignore

    # 添加 pytest.mark.use_generators 标记
    func.pytestmark = getattr(func, "pytestmark", [])  # type: ignore
    func.pytestmark.append(pytest.mark.use_generators)  # type: ignore

    return func
