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


class TestWithFixture:
    """测试使用fixture的测试类"""
    
    @with_dynamic_params(user_data=get_user_data)
    @pytest.mark.parametrize("user_type", ["admin", "user"])
    def test_with_fixture(self, database, user_type, user_data):
        """测试用例数量：2个"""
        assert user_data["type"] == user_type
        assert database["users"][user_type] is not None
