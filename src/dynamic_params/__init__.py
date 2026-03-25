# 所有模块级导入放在文件顶部
from .engine.config import DynamicParamConfig
from .engine.dependency import (
    CircularDependencyError,
    resolve_dependency_order
)
from .engine.registry import GeneratorRegistry
from .errors import (
    ConfigurationError,
    DynamicParamError,
    ExecutionError,
    InvalidGeneratorError,
    MissingParameterError,
)
from .plugin import pytest_configure, pytest_generate_tests
from .public.decorators.dynamic_parametrize import DynRef, dynamic_parametrize
from .public.decorators.generator import generator as generator_decorator
from .public.decorators.use_generators import use_generators
from .public.generators.generator import Generator
from .public.generators.lazy import LazyResult, generate_lazy_combinations
from .utils.helpers import normalize_param_value, validate_param_name

# 重命名装饰器以避免与模块名冲突
generator = generator_decorator

__all__ = [
    "Generator",
    "LazyResult",
    "generate_lazy_combinations",
    "GeneratorRegistry",
    "DynamicParamError",
    "MissingParameterError",
    "InvalidGeneratorError",
    "ConfigurationError",
    "ExecutionError",
    "generator",
    "use_generators",
    "dynamic_parametrize",
    "DynRef",
    "pytest_configure",
    "pytest_generate_tests",
    "DynamicParamConfig",
    "resolve_dependency_order",
    "CircularDependencyError",
    "normalize_param_value",
    "validate_param_name",
]

# 移除了向后兼容的 ParamGenerator 导入
