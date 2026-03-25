import inspect
from typing import Any, Callable, Dict, List, Optional, TypeVar

T = TypeVar("T")


class Generator:
    """
    生成器类，封装生成器的核心逻辑
    """

    def __init__(
        self,
        func: Callable,
        name: str,
        scope: str = "function",
        cache_enabled: bool = True,
        lazy_support: bool = True,
    ):
        self.func = func
        self.name = name
        self.scope = scope
        self.cache_enabled = cache_enabled
        self.lazy_support = lazy_support
        self.stats = {"hits": 0, "misses": 0, "executions": 0}
        self.dependencies = self._extract_dependencies(func)
        self._input_values: Optional[List[Any]] = None

    def get_result(self, context: Dict[str, Any]) -> Any:
        """获取生成结果"""
        from ...engine.registry import GeneratorRegistry

        registry = GeneratorRegistry.get_instance()
        self._check_dependencies(context)

        if not self.lazy_support:
            return self._get_result_without_lazy(context, registry)
        else:
            return self._get_result_with_lazy(context, registry)

    def _check_dependencies(self, context: Dict[str, Any]) -> None:
        """检查依赖是否存在"""
        missing = [dep for dep in self.dependencies if dep not in context]
        if missing:
            from ...errors import MissingParameterError

            raise MissingParameterError(
                param_name=missing[0],
                generator_name=self.func.__name__,
                required_params=self.dependencies,
                available_params=list(context.keys()),
            )

    def _get_result_without_lazy(
        self,
        context: Dict[str, Any],
        registry
    ) -> Any:
        """处理非懒加载模式"""
        cache_key = self._make_cache_key(context)
        cached_result = self._check_cache(cache_key, registry)
        if cached_result is not None:
            return cached_result

        self.stats["misses"] += 1
        result = self._execute_generator(context)
        self._store_cache(cache_key, result, registry)
        return result

    def _get_result_with_lazy(
        self,
        context: Dict[str, Any],
        registry
    ) -> Any:
        """处理懒加载模式"""
        from .lazy import LazyResult

        cache_key = self._make_cache_key(context)
        cached_result = self._check_cache(cache_key, registry)
        if cached_result is not None:
            return cached_result

        self.stats["misses"] += 1
        lazy_result = LazyResult(
            generator=self,
            context=context,
            cache_key=cache_key
        )
        self._store_cache(cache_key, lazy_result, registry)
        return lazy_result

    def _check_cache(self, cache_key: str, registry) -> Any:
        """检查缓存"""
        if not self.cache_enabled:
            return None

        # 检查作用域缓存
        scoped_cache = registry.get_scoped_cache(
            self.scope
        )
        if cache_key in scoped_cache:
            self.stats["hits"] += 1
            return scoped_cache[cache_key]
        return None

    def _store_cache(self, cache_key: str, result: Any, registry) -> None:
        """存储缓存"""
        if not self.cache_enabled:
            return

        # 存储到作用域缓存
        scoped_cache = registry.get_scoped_cache(
            self.scope
        )
        scoped_cache[cache_key] = result

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
            if param.name
            not in {"request", "metafunc", "item", "config", "self", "cls"}
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
        return f"{self.name}:{hash(dep_values)}"

    def _prepare_kwargs(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """准备生成器调用参数"""
        missing = [dep for dep in self.dependencies if dep not in context]
        if missing:
            from ...errors import MissingParameterError

            raise MissingParameterError(
                param_name=missing[0],
                generator_name=self.func.__name__,
                required_params=self.dependencies,
                available_params=list(context.keys()),
            )
        return {k: context[k] for k in self.dependencies}

    def register_input_values(self, values: List[Any]) -> None:
        """注册输入参数值"""
        self._input_values = values
