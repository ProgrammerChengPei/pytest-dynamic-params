"""参数生成器注册表模块"""

from typing import Any, Callable, Dict, List, Optional

from ..errors import InvalidGeneratorError
from ..public.generators.generator import Generator


class GeneratorRegistry:
    """生成器注册表（单例）"""

    _instance: Optional["GeneratorRegistry"] = None
    _generators: Dict[str, Generator]
    _param_to_generator: Dict[str, str]
    _scoped_caches: Dict[str, Dict[str, Any]]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._generators = {}
            cls._instance._param_to_generator = {}
            # 按作用域管理缓存
            cls._instance._scoped_caches = {
                "function": {},
                "class": {},
                "module": {},
                "session": {},
            }
        return cls._instance

    @classmethod
    def get_instance(cls):
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def is_registered_by_function_name(self, func_name: str) -> bool:
        """通过函数名检查是否有生成器已注册"""
        # 遍历所有生成器，检查是否有函数名匹配的
        for generator_key in self._generators:
            # 从键中提取函数名
            parts = generator_key.split(":")
            if len(parts) >= 2 and parts[1] == func_name:
                return True
        return False

    def is_registered_by_function_object(
        self,
        generator_func: Callable
    ) -> bool:
        """通过函数对象检查是否已注册"""
        # 遍历所有生成器，检查是否有使用相同函数的
        for generator in self._generators.values():
            actual_func = generator_func
            while hasattr(actual_func, "__wrapped__"):
                actual_func = actual_func.__wrapped__

            generator_actual_func = generator.func
            while hasattr(generator_actual_func, "__wrapped__"):
                generator_actual_func = generator_actual_func.__wrapped__

            if actual_func == generator_actual_func:
                return True
        return False

    def register(self, generator_func: Callable, name: str) -> Generator:
        """注册生成器函数

        参数:
            generator_func: 生成器函数，必须用@generator装饰
            name: 参数名称

        返回:
            注册后的Generator实例
        """
        # 获取实际的生成器函数（跳过包装层）
        actual_func = generator_func
        while hasattr(actual_func, "__wrapped__"):
            actual_func = actual_func.__wrapped__

        # 验证函数是否由@generator装饰
        if not hasattr(actual_func, "_decorator_args"):
            raise InvalidGeneratorError(
                f"函数 {generator_func.__name__} 不是参数生成器"
            )

        # 为每个生成器函数和参数名组合创建唯一的键
        # 使用函数的完全限定名（包含模块名）来确保唯一性
        module_name = getattr(actual_func, "__module__", "unknown")
        unique_key = f"{module_name}:{actual_func.__name__}:{name}"

        # 如果已经注册过，直接返回
        if unique_key in self._generators:
            return self._generators[unique_key]

        # 创建Generator实例
        generator = Generator(
            func=actual_func,
            name=name,
            scope=getattr(actual_func, "_scope", "function"),
            cache_enabled=getattr(actual_func, "_cache_enabled", True),
            lazy_support=getattr(actual_func, "_lazy_support", True),
        )

        # 存储生成器实例，使用唯一键
        self._generators[unique_key] = generator
        # 存储参数名到唯一键的映射
        self._param_to_generator[name] = unique_key
        return generator

    def get_generator(self, param_name: str) -> Optional[Generator]:
        """通过参数名获取生成器"""
        if param_name not in self._param_to_generator:
            return None

        generator_key = self._param_to_generator[param_name]
        return self._generators.get(generator_key)

    def get_all_generators(self) -> List[Generator]:
        """获取所有已注册的生成器"""
        return list(self._generators.values())

    def clear_cache(self, scope: Optional[str] = None):
        """清理缓存"""
        if scope is None:
            # 清理所有作用域的缓存
            for s in ["function", "class", "module", "session"]:
                self._scoped_caches[s].clear()
        else:
            # 清理指定作用域的缓存
            if scope in self._scoped_caches:
                self._scoped_caches[scope].clear()

    def get_scoped_cache(self, scope: str):
        """获取指定作用域的缓存"""
        return self._scoped_caches.get(scope, {})

    def set_scoped_cache(self, scope: str, cache: dict):
        """设置指定作用域的缓存"""
        if scope in self._scoped_caches:
            self._scoped_caches[scope] = cache
