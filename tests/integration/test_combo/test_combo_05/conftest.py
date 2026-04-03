"""5 组合测试 - 共享配置"""
import pytest


@pytest.fixture
def combo_fixture_5():
    """5 组合 fixture"""
    return {"level": 5, "complete": True}
