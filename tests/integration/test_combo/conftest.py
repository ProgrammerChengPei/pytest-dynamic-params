"""
pytest-dynamic-params 组合集成测试 - 共享配置
"""

import pytest


@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "id": 1,
        "name": "Test User",
        "email": "test@example.com"
    }


@pytest.fixture
def sample_product_data():
    """示例产品数据"""
    return {
        "id": 1,
        "name": "Test Product",
        "price": 99.99
    }


@pytest.fixture
def sample_order_data():
    """示例订单数据"""
    return {
        "id": 1,
        "user_id": 1,
        "total": 199.98
    }


@pytest.fixture
def base_config():
    """基础配置"""
    return {
        "api_url": "http://localhost:8000",
        "timeout": 30,
        "debug": True
    }


@pytest.fixture
def environment():
    """环境配置"""
    return "test"


@pytest.fixture
def multiplier():
    """乘数 fixture"""
    return 2


@pytest.fixture
def base_value():
    """基础值 fixture"""
    return 10
