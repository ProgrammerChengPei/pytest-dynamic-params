"""公共接口模块"""

# 从 decorators 导入
from .decorators.dynamic_parametrize import DynRef, dynamic_parametrize
from .decorators.generator import generator
from .decorators.use_generators import use_generators

# 从 generators 导入
from .generators.generator import Generator
from .generators.lazy import LazyResult, generate_lazy_combinations

__all__ = [
    "generator",
    "use_generators",
    "dynamic_parametrize",
    "DynRef",
    "Generator",
    "LazyResult",
    "generate_lazy_combinations",
]
