# 统一装饰器接口定义
"""
pytest-dynamic-params装饰器接口

提供简洁、一致的装饰器API，实现参数化测试的核心功能。
"""

from typing import Callable, Optional, Union
from typing_extensions import overload

from ..services.generator_service import GeneratorService
from ..services.parametrization_service import ParametrizationService


class DecoratorInterface:
    """装饰器统一接口类"""
    
    def __init__(self):
        self.generator_service = GeneratorService()
        self.parametrization_service = ParametrizationService()
    
    @overload
    def param_generator(self, func: Callable) -> Callable:
        """无参数装饰器用法：@param_generator"""
        pass
    
    @overload
    def param_generator(self, *, 
                       scope: Optional[str] = None,
                       cache: bool = False,
                       lazy: bool = False) -> Callable[[Callable], Callable]:
        """带参数装饰器用法：@param_generator(scope="session", cache=True)"""
        pass
    
    def param_generator(self, 
                       func: Optional[Callable] = None,
                       *, 
                       scope: Optional[str] = None,
                       cache: bool = False,
                       lazy: bool = False) -> Union[Callable, Callable[[Callable], Callable]]:
        """
        链式参数生成器装饰器
        
        功能特性：
        - 智能作用域推断：根据依赖关系自动选择最小scope
        - 缓存支持：配置生成器结果缓存以提高性能
        - 懒加载：延迟执行提高启动速度
        - 依赖管理：与pytest参数化装饰器链式组合
        
        Args:
            func: 生成器函数
            scope: 作用域级别 ("function", "class", "module", "session")
            cache: 是否启用缓存
            lazy: 是否启用懒加载
            
        Returns:
            装饰后的生成器函数
        """
        def decorator(f: Callable) -> Callable:
            return self.generator_service.create_generator(f, scope, cache, lazy)
        
        if func is None:
            return decorator
        return decorator(func)
    
    def parametrize_fixture(self,
                           scope: str = "function",
                           *,
                           params: Optional[list] = None,
                           autouse: bool = False,
                           ids: Optional[Callable] = None,
                           name: Optional[str] = None) -> Callable:
        """
        参数化fixture装饰器
        
        创建支持参数化的pytest fixture，可与其他生成器链式组合使用。
        
        Args:
            scope: fixture作用域
            params: 参数列表
            autouse: 是否自动使用
            ids: 参数ID生成函数
            name: fixture名称
            
        Returns:
            装饰器函数
        """
        def decorator(func: Callable) -> Callable:
            return self.parametrization_service.create_parametrized_fixture(
                func, scope, params, autouse, ids, name
            )
        return decorator


# 创建全局接口实例
_interface = DecoratorInterface()

# 导出装饰器函数
param_generator = _interface.param_generator
parametrize_fixture = _interface.parametrize_fixture