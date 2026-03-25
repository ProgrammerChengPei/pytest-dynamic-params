"""处理器模块初始化文件"""

from .dynamic_parametrize import process_dynamic_parametrize
from .use_generators import process_use_generators

__all__ = [
    "process_use_generators",
    "process_dynamic_parametrize",
]
