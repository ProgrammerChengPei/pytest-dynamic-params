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
        if not self.lazy_support:
            return self._execute_generator(context)
            
        if self.cache_enabled:
            cache_key = self._make_cache_key(context)
            if cache_key in self._cache:
                self.stats["hits"] += 1
                return self._cache[cache_key]
                
        self.stats["misses"] += 1
        result = self._execute_generator(context)
        
        if self.cache_enabled:
            self._cache[self._make_cache_key(context)] = result
            
        return result
        
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