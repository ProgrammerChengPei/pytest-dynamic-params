"""@dynamic_parametrize 装饰器处理器"""

from typing import Any, Callable, Dict, Tuple

import pytest


def process_dynamic_parametrize(
    func: Callable, args: Tuple, kwargs: Dict[str, Any]
) -> Callable:
    """处理 @dynamic_parametrize 装饰器

    Args:
        func: 被装饰的函数
        args: 位置参数
        kwargs: 关键字参数

    Returns:
        处理后的函数
    """
    # 为函数添加标记，以便 pytest_generate_tests 钩子识别
    func._is_parametrized = True  # type: ignore

    # 存储参数化信息
    if not hasattr(func, "_parametrize_info"):
        func._parametrize_info = []  # type: ignore

    func._parametrize_info.append(
        {"args": args, "kwargs": kwargs}
    )  # type: ignore

    # 添加 pytest.mark.dynamic_parametrize 标记
    func.pytestmark = getattr(func, "pytestmark", [])  # type: ignore
    func.pytestmark.append(pytest.mark.dynamic_parametrize)  # type: ignore

    return func
