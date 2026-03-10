import inspect
from typing import Any, Callable, Dict, List, TypeVar

T = TypeVar('T')

class ParamGenerator:
    """
    参数生成器类，封装参数生成器的核心逻辑
    """
    
    def __init__(self, 
                 func: Callable, 
                 param_name: str, 
                 scope: str = "function", 
                 cache_enabled: bool = True, 
                 lazy_support: bool = True):
        self.func = func
        self.param_name = param_name
        self.scope = scope
        self.cache_enabled = cache_enabled
        self.lazy_support = lazy_support
        self._cache: Dict[str, Any] = {}
        self.stats = {"hits": 0, "misses": 0, "executions": 0}
        self.dependencies = self._extract_dependencies(func)
        self._input_values = None
        
    def get_result(self, context: Dict[str, Any]) -> Any:
        """获取生成结果"""
        from ..core.registry import GeneratorRegistry
        registry = GeneratorRegistry.get_instance()
        
        if not self.lazy_support:
            # 非懒加载模式，直接执行
            if self.cache_enabled:
                cache_key = self._make_cache_key(context)
                # 检查作用域缓存
                scoped_cache = registry.get_scoped_cache(self.scope)
                if cache_key in scoped_cache:
                    self.stats["hits"] += 1
                    return scoped_cache[cache_key]
                # 检查本地缓存（向后兼容）
                elif cache_key in self._cache:
                    self.stats["hits"] += 1
                    return self._cache[cache_key]
                    
            self.stats["misses"] += 1
            result = self._execute_generator(context)
            
            if self.cache_enabled:
                # 存储到作用域缓存
                scoped_cache = registry.get_scoped_cache(self.scope)
                scoped_cache[cache_key] = result
                # 存储到本地缓存（向后兼容）
                self._cache[cache_key] = result
                
            return result
        else:
            # 懒加载模式，返回LazyResult对象
            from ..lazy import LazyResult
            cache_key = self._make_cache_key(context)
            
            # 检查缓存
            if self.cache_enabled:
                # 检查作用域缓存
                scoped_cache = registry.get_scoped_cache(self.scope)
                if cache_key in scoped_cache:
                    self.stats["hits"] += 1
                    return scoped_cache[cache_key]
                # 检查本地缓存（向后兼容）
                elif cache_key in self._cache:
                    self.stats["hits"] += 1
                    return self._cache[cache_key]
            
            # 生懒加载结果
            self.stats["misses"] += 1
            lazy_result = LazyResult(
                generator=self,
                context=context,
                cache_key=cache_key
            )
            
            # 缓存懒加载结果
            if self.cache_enabled:
                # 存储到作用域缓存
                scoped_cache = registry.get_scoped_cache(self.scope)
                scoped_cache[cache_key] = lazy_result
                # 存储到本地缓存（向后兼容）
                self._cache[cache_key] = lazy_result
                
            return lazy_result
        
    def _execute_generator(self, context: Dict[str, Any]) -> Any:
        """执行生成器函数"""
        self.stats["executions"] += 1
        kwargs = self._prepare_kwargs(context)
        return self.func(**kwargs)
    
    @staticmethod
    def _extract_dependencies(func: Callable) -> List[str]:
        """从函数签名提取依赖参数"""
        sig = inspect.signature(func)
        return [
            param.name 
            for param in sig.parameters.values() 
            if param.name not in {"request", "metafunc", "item", "config", "self", "cls"}
        ]
    
    def _make_cache_key(self, context: Dict[str, Any]) -> str:
        """生成缓存键"""
        import json

        # 将上下文转换为可哈希的字符串
        dep_values = tuple(
            (dep, json.dumps(context[dep], sort_keys=True, default=str))
            for dep in self.dependencies
            if dep in context
        )
        return f"{self.param_name}:{hash(dep_values)}"
    
    def _prepare_kwargs(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """准备生成器调用参数"""
        missing = [dep for dep in self.dependencies if dep not in context]
        if missing:
            from ..errors import MissingParameterError
            raise MissingParameterError(
                param_name=missing[0],
                generator_name=self.func.__name__,
                required_params=self.dependencies,
                available_params=list(context.keys())
            )
        return {k: context[k] for k in self.dependencies}
        
    def register_input_values(self, values: List[Any]) -> None:
        """注册输入参数值"""
        self._input_values = values