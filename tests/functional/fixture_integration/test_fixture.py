"""
示例2: 混合参数（含普通fixture）
对应 specs/需求.md 第314-330行的使用示例
"""

import pytest

from dynamic_params import with_dynamic_params
from tests.generators import get_user_data


# 定义普通fixture
@pytest.fixture
def database():
    """模拟数据库连接"""
    db = {"users": {"admin": {"type": "admin"}, "user": {"type": "user"}}}
    yield db
    # 清理代码
    db.clear()


# 测试边界情况：fixture返回空字典
@pytest.fixture
def empty_database():
    """返回空数据库"""
    return {"users": {}}


class TestFixture:
    """测试使用fixture的测试类"""

    @with_dynamic_params(user_data=get_user_data)
    @pytest.mark.parametrize("user_type", ["admin", "user"])
    def test_fixture_integration(self, database, user_type, user_data):
        """测试用例数量：2个"""
        assert user_data["type"] == user_type
        assert database["users"][user_type] is not None


class TestFixtureEdgeCases:
    """测试使用fixture的边界情况"""

    # 测试错误情况：不存在的用户类型
    @with_dynamic_params(user_data=get_user_data)
    @pytest.mark.parametrize("user_type", ["guest"])
    def test_fixture_nonexistent_user(
        self, empty_database, user_type, user_data
    ):
        """测试不存在的用户类型"""
        # 这里期望get_user_data会处理这种情况
        # 假设get_user_data会返回None或抛出异常
        # 根据实际实现调整断言
