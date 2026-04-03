"""3 组合测试 - 共享配置"""
import pytest


@pytest.fixture
def combo_fixture():
    """3 组合 fixture"""
    return {"level": 3}
