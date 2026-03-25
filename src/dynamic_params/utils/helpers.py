"""辅助函数模块"""

import inspect
import json
from typing import Any, Callable, Dict, List


def validate_generator_function(func: Callable) -> bool:
    """验证函数是否是有效的生成器函数

    Args:
        func: 函数对象

    Returns:
        是否是有效的生成器函数
    """
    if not callable(func):
        return False

    # 检查函数是否有 _is_generator 属性
    if hasattr(func, "_is_generator") and func._is_generator:
        return True

    # 检查函数是否被 @generator 装饰器装饰
    actual_func = func
    while hasattr(actual_func, "__wrapped__"):
        actual_func = actual_func.__wrapped__
        if hasattr(actual_func, "_is_generator") and actual_func._is_generator:
            return True

    return False


def get_function_signature(func: Callable) -> inspect.Signature:
    """获取函数签名

    Args:
        func: 函数对象

    Returns:
        函数签名
    """
    actual_func = func
    while hasattr(actual_func, "__wrapped__"):
        actual_func = actual_func.__wrapped__
    return inspect.signature(actual_func)


def extract_function_name(func: Callable) -> str:
    """提取函数名称

    Args:
        func: 函数对象

    Returns:
        函数名称
    """
    actual_func = func
    while hasattr(actual_func, "__wrapped__"):
        actual_func = actual_func.__wrapped__
    return actual_func.__name__


def is_valid_scope(scope: str) -> bool:
    """检查作用域是否有效

    Args:
        scope: 作用域字符串

    Returns:
        是否是有效的作用域
    """
    valid_scopes = ["function", "class", "module", "session"]
    return scope in valid_scopes


def normalize_scope(scope: str) -> str:
    """标准化作用域

    Args:
        scope: 作用域字符串

    Returns:
        标准化后的作用域
    """
    if is_valid_scope(scope):
        return scope
    return "function"  # 默认作用域


def create_cache_key(context: Dict[str, Any], dependencies: List[str]) -> str:
    """创建缓存键

    Args:
        context: 上下文字典
        dependencies: 依赖列表

    Returns:
        缓存键
    """
    # 将上下文转换为可哈希的字符串
    dep_values = tuple(
        (dep, json.dumps(context.get(dep), sort_keys=True, default=str))
        for dep in dependencies
    )
    return f"{hash(dep_values)}"


def normalize_param_value(value: Any) -> Any:
    """标准化参数值

    Args:
        value: 参数值

    Returns:
        标准化后的值
    """
    # 对于字符串，去除首尾空格
    if isinstance(value, str):
        return value.strip()
    # 对于其他类型，直接返回
    return value


def validate_param_name(name: str) -> bool:
    """验证参数名是否有效

    Args:
        name: 参数名

    Returns:
        是否是有效的参数名
    """
    # 检查是否是字符串
    if not isinstance(name, str):
        return False
    # 检查是否为空
    if not name:
        return False
    # 检查是否是有效的Python标识符
    return name.isidentifier()
