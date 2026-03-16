"""
测试fixture
"""

import pytest


# 测试fixture
@pytest.fixture
def test_value():
    """测试值fixture"""
    return 42


@pytest.fixture
def test_list():
    """测试列表fixture"""
    return [1, 2, 3, 4, 5]
