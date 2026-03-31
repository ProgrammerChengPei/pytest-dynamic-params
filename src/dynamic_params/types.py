# Type definitions for pytest-dynamic-params

from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    TypeVar,
    Union,
    Generator as GeneratorType,
)

# Type variables
T = TypeVar('T')

# Generator function type
GeneratorFunc = Callable[..., Union[List[Any], GeneratorType[Any, None, None]]]

# Parameter value type
ParamValue = Union[Any, 'DynRef']

# Parameter values type
ParamValues = List[List[ParamValue]]

# Parametrization configuration type
ParametrizationConfig = Dict[str, Any]

# Dependency graph type
DependencyGraphType = Dict[str, Dict[str, List[str]]]

# Cache type
CacheType = Dict[str, Dict[str, Any]]

# Context type
ContextType = Dict[str, Any]
