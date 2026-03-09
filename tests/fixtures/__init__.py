"""测试fixtures模块"""

from .config import app_config, base_config, database_config
from .database import database
from .environment import environment

__all__ = [
    'database',
    'environment',
    'base_config',
    'database_config',
    'app_config'
]
