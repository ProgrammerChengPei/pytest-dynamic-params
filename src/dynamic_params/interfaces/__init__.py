# 统一接口层模块初始化
"""
pytest-dynamic-params接口层模块

该模块提供统一的用户可见API和类型定义，包括：
- 装饰器接口：param_generator, parametrize_fixture等
- 配置接口：配置获取和设置方法
- 类型定义：用户需要使用的类型

使用示例：
    from dynamic_params.interfaces import param_generator, parametrize_fixture
    
    # 使用装饰器
    @param_generator(scope="session")
    def data_source():
        return [1, 2, 3]
"""

from .decorators import param_generator, parametrize_fixture
from .config import get_config, set_config, configure
from .types import GeneratorFunc, ParamConfig

__all__ = [
    "param_generator",
    "parametrize_fixture", 
    "get_config",
    "set_config",
    "configure",
    "GeneratorFunc",
    "ParamConfig",
]