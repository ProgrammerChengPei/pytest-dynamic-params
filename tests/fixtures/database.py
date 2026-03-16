"""数据库相关fixtures"""

import pytest


@pytest.fixture
def database():
    """模拟数据库连接"""
    db = {"users": {"admin": {"type": "admin"}, "user": {"type": "user"}}}
    yield db
    # 清理代码
    db.clear()
