"""公共接口模块"""

from .decorators.param_generator import param_generator
from .decorators.parametrize_fixture import parametrize_fixture

__all__ = [
    "parametrize_fixture",
    "param_generator",
]
