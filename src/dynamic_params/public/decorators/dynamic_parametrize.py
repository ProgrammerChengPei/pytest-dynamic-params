import functools
from typing import Any, Callable, Dict

from ...plugin.processors import process_dynamic_parametrize


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
        elif (self.ref_type == "fixture" and
              hasattr(request, "getfixturevalue")):
            return request.getfixturevalue(self.name)
        else:
            raise ValueError(f"无法解析引用: {self.name}")


def dynamic_parametrize(*param_args, **param_kwargs):
    """
    动态参数化装饰器，替代 pytest.mark.parametrize
    支持在参数化中使用 DynRef 引用其他参数和 fixture

    Args:
        *param_args: 与 pytest.mark.parametrize 相同的参数格式
        **param_kwargs: 与 pytest.mark.parametrize 相同的关键字参数
    """

    def decorator(func: Callable) -> Callable:
        # 使用处理器处理装饰器逻辑
        processed_func = process_dynamic_parametrize(
            func, param_args, param_kwargs
        )

        @functools.wraps(processed_func)
        def wrapper(*args, **kwargs):
            return processed_func(*args, **kwargs)

        # 为包装函数设置相同的动态参数化属性
        wrapper._parametrize_info = (
            processed_func._parametrize_info
        )  # type: ignore
        wrapper._is_parametrized = (
            processed_func._is_parametrized
        )  # type: ignore
        wrapper.pytestmark = getattr(
            processed_func,
            "pytestmark",
            []
        )  # type: ignore

        return wrapper

    return decorator
