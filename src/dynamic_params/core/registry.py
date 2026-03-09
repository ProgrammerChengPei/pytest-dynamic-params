"""参数生成器注册表模块"""

from typing import List, Optional

from .generator import ParamGenerator


class GeneratorRegistry:
    """生成器注册表（单例）"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._generators = {}
            cls._instance._param_to_generator = {}
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def is_registered(self, func_name: str) -> bool:
        """检查生成器函数名是否已注册"""
        return func_name in self._generators
        
    def is_generator_registered(self, generator_func: 'Callable') -> bool:
        """检查生成器函数是否已注册（通过函数对象）"""
        # 获取实际的生成器函数（跳过包装层）
        actual_func = generator_func
        while hasattr(actual_func, '__wrapped__'):
            actual_func = actual_func.__wrapped__
            
        return actual_func.__name__ in self._generators
    
    def register(self, generator_func: 'Callable', param_name: str) -> ParamGenerator:
        """注册生成器函数
        
        参数:
            generator_func: 生成器函数，必须用@param_generator装饰
            param_name: 参数名称
            
        返回:
            注册后的ParamGenerator实例
        """
        # 获取实际的生成器函数（跳过包装层）
        actual_func = generator_func
        while hasattr(actual_func, '__wrapped__'):
            actual_func = actual_func.__wrapped__
            
        # 验证函数是否由@param_generator装饰
        if not hasattr(actual_func, '_decorator_args'):
            raise InvalidGeneratorError(f"函数 {generator_func.__name__} 不是参数生成器")
            
        # 允许同一生成器注册为不同参数
        if actual_func.__name__ in self._generators:
            existing = self._generators[actual_func.__name__]
            if existing.param_name == param_name:
                return existing
            
            # 创建新的ParamGenerator实例用于新参数
            generator = ParamGenerator(
                func=actual_func,
                param_name=param_name,
                scope=getattr(actual_func, '_scope', 'function'),
                cache_enabled=getattr(actual_func, '_cache_enabled', True),
                lazy_support=getattr(actual_func, '_lazy_support', True)
            )
            self._param_to_generator[param_name] = actual_func.__name__
            return generator
            
        # 创建ParamGenerator实例
        generator = ParamGenerator(
            func=actual_func,
            param_name=param_name,
            scope=getattr(actual_func, '_scope', 'function'),
            cache_enabled=getattr(actual_func, '_cache_enabled', True),
            lazy_support=getattr(actual_func, '_lazy_support', True)
        )
        
        self._generators[actual_func.__name__] = generator
        self._param_to_generator[param_name] = actual_func.__name__
        return generator
    
    def get_generator(self, param_name: str) -> Optional[ParamGenerator]:
        """通过参数名获取生成器"""
        if param_name not in self._param_to_generator:
            return None
            
        generator_name = self._param_to_generator[param_name]
        return self._generators.get(generator_name)
    
    def get_all_generators(self) -> List[ParamGenerator]:
        """获取所有已注册的生成器"""
        return list(self._generators.values())
    
    def clear_cache(self, scope: Optional[str] = None):
        """清理缓存"""
        for generator in self._generators.values():
            if scope is None or generator.scope == scope:
                generator._cache.clear()


# Import error classes here to avoid circular imports
from ..errors import InvalidGeneratorError
