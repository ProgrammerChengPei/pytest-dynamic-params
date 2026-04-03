"""4 组合测试 - 共享配置"""
import pytest


@pytest.fixture
def combo_fixture_4():
    """4 组合 fixture"""
    return {"level": 4}
