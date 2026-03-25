"""类型定义模块"""

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Literal,
    TypeVar,
)

# 类型变量
T = TypeVar("T")

# 生成器函数类型
GeneratorFunction = Callable[..., Any]

# 上下文类型
Context = Dict[str, Any]

# 生成器映射类型
GeneratorMapping = Dict[str, GeneratorFunction]

# 作用域类型
ScopeType = Literal["function", "class", "module", "session"]

# 参数化信息类型
ParametrizeInfo = Dict[str, Any]

# 生成器注册表类型
GeneratorRegistryType = "GeneratorRegistry"

# 生成器类型
if TYPE_CHECKING:
    from .public.generators.generator import Generator

GeneratorType = "Generator"

# 懒加载结果类型
LazyResultType = "LazyResult"

# 装饰器参数类型
DecoratorArgs = Dict[str, Any]

# 配置类型
ConfigDict = Dict[str, Dict[str, Any]]

# 依赖顺序类型
DependencyOrder = List["Generator"]

# 缓存键类型
CacheKey = str

# 作用域缓存类型
ScopedCache = Dict[CacheKey, Any]

# 作用域缓存映射类型
ScopedCacheMap = Dict[ScopeType, ScopedCache]
