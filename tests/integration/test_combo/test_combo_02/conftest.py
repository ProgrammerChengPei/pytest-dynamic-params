"""2 组合测试 - 共享配置"""
import pytest


@pytest.fixture
def fixture_value():
    """fixture 值"""
    return "fixture_value"


@pytest.fixture
def numeric_fixture():
    """数值 fixture"""
    return 42
