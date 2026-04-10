# 服务层模块初始化
"""
pytest-dynamic-params服务层模块

该模块封装插件的核心业务逻辑，提供稳定、可测试的服务接口：
- GeneratorService: 生成器生命周期管理
- ParametrizationService: 参数化处理服务
- DependencyService: 依赖解析服务
- CacheService: 缓存管理服务

服务层是业务逻辑的核心，提供接口层和引擎层之间的桥梁。
"""

from .generator_service import GeneratorService
from .parametrization_service import ParametrizationService
from .dependency_service import DependencyService
from .cache_service import CacheService

__all__ = [
    "GeneratorService",
    "ParametrizationService", 
    "DependencyService",
    "CacheService",
]