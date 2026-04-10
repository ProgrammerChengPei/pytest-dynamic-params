# 生成器服务 - 核心业务逻辑实现
"""
生成器服务负责管理参数生成器的完整生命周期，包括：
- 生成器创建和注册
- 作用域管理
- 依赖解析
- 执行优化

该服务是插件最核心的业务逻辑实现。
"""

from typing import Callable, Optional, List, Any
import inspect
import logging

from ..engines.core_engine import CoreEngine
from ..exceptions import ConfigurationError, GenerationError
from ..interfaces.types import GeneratorConfig


class GeneratorService:
    """生成器服务主类"""
    
    def __init__(self):
        self.engine = CoreEngine()
        self.logger = logging.getLogger(__name__)
        self._registry = {}  # 生成器注册表
    
    def create_generator(self, 
                        func: Callable,
                        scope: Optional[str] = None,
                        cache: bool = False,
                        lazy: bool = False) -> Callable:
        """
        创建并注册参数生成器
        
        Args:
            func: 生成器函数
            scope: 作用域级别
            cache: 是否启用缓存
            lazy: 是否启用懒加载
            
        Returns:
            装饰后的生成器函数
        """
        self.logger.debug(f"Creating generator for {func.__name__}")
        
        # 验证函数签名
        self._validate_generator_function(func)
        
        # 推断作用域
        final_scope = self._infer_scope(func, scope)
        
        # 创建配置
        config = GeneratorConfig(
            scope=final_scope,
            cache=cache,
            lazy=lazy,
            func_name=func.__name__
        )
        
        # 注册到引擎
        generator_id = self.engine.register_generator(func, config)
        
        # 返回包装函数
        def generator_wrapper(*args, **kwargs):
            return self.execute_generator(generator_id, *args, **kwargs)
        
        # 保留原始函数属性
        generator_wrapper.__name__ = func.__name__
        generator_wrapper.__doc__ = func.__doc__
        generator_wrapper._generator_id = generator_id
        
        return generator_wrapper
    
    def execute_generator(self, generator_id: str, *args, **kwargs) -> List[Any]:
        """
        执行指定生成器
        
        Args:
            generator_id: 生成器标识
            *args: 生成器参数
            **kwargs: 生成器关键字参数
            
        Returns:
            生成的参数列表
        """
        try:
            return self.engine.execute_generator(generator_id, *args, **kwargs)
        except Exception as e:
            self.logger.error(f"Generator {generator_id} execution failed: {e}")
            raise GenerationError(f"Failed to execute generator {generator_id}") from e
    
    def _validate_generator_function(self, func: Callable) -> None:
        """验证生成器函数符合要求"""
        if not callable(func):
            raise ConfigurationError("Generator must be a callable function")
        
        # 检查函数签名
        sig = inspect.signature(func)
        params = sig.parameters
        
        # 生成器函数应该返回可迭代数据
        # 这里可以添加更复杂的验证逻辑
        
    def _infer_scope(self, func: Callable, explicit_scope: Optional[str]) -> str:
        """推断生成器作用域"""
        if explicit_scope:
            return explicit_scope
        
        # 智能推断逻辑
        # 1. 检查是否有依赖关系
        # 2. 检查函数复杂度
        # 3. 默认使用session级以获得最佳性能
        
        # 简化实现：先检查是否使用装饰器
        source = inspect.getsource(func)
        
        if '@pytest.mark.parametrize' in source:
            # 有依赖关系的生成器使用更严格的作用域
            return "function"
        
        # 无依赖的生成器使用session级别
        return "session"
    
    def get_generator_info(self, generator_id: str) -> dict:
        """获取生成器详细信息"""
        return self.engine.get_generator_info(generator_id)
    
    def list_generators(self) -> List[dict]:
        """列出所有注册的生成器"""
        return self.engine.list_generators()
    
    def cleanup(self):
        """清理生成器资源"""
        self.engine.cleanup()
        self._registry.clear()