"""工具函数模块"""


def get_function_signature(func) -> str:
    """获取函数签名字符串"""
    import inspect
    sig = inspect.signature(func)
    return f"{func.__name__}{sig}"


def validate_param_name(param_name: str) -> bool:
    """验证参数名称是否合法"""
    if not param_name or not isinstance(param_name, str):
        return False
    # 检查是否为有效的Python标识符
    return param_name.isidentifier()


def normalize_param_value(value):
    """标准化参数值"""
    # 这里可以添加参数值的标准化逻辑
    return value