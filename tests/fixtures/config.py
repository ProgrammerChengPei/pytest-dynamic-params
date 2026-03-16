"""配置相关fixtures"""

import pytest


@pytest.fixture
def base_config():
    """基础配置"""
    return {"app": "test", "version": "1.0"}


@pytest.fixture
def database_config(base_config):
    """数据库配置（依赖base_config）"""
    return {**base_config, "db": "postgresql"}


@pytest.fixture
def app_config(database_config):
    """应用配置（依赖database_config）"""
    return {**database_config, "port": 8080}
