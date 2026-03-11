"""
示例4: 多个fixture嵌套
对应 specs/需求.md 第354-376行的使用示例
"""

import pytest

from dynamic_params import with_dynamic_params
from tests.generators import generate_test_data


# 定义嵌套fixture
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


class TestNestedFixtures:
    """测试嵌套fixtures的测试类"""

    @with_dynamic_params(test_data=generate_test_data)
    @pytest.mark.parametrize("test_type", ["unit", "integration"])
    def test_fixture_nesting(self, app_config, test_type, test_data):
        """fixture依赖链：
        base_config → database_config → app_config → generate_test_data
        """
        assert test_data["config"]["port"] == 8080
        assert test_data["type"] == test_type
        assert len(test_data["data"]) == 3

    # 测试边界情况：不同的测试类型
    @with_dynamic_params(test_data=generate_test_data)
    @pytest.mark.parametrize("test_type", ["", None, "smoke"])
    def test_fixture_nesting_edge_cases(
        self, app_config, test_type, test_data
    ):
        """测试边界情况：空和None测试类型"""
        assert test_data["config"]["port"] == 8080
        assert test_data["type"] == test_type
        assert len(test_data["data"]) == 3
