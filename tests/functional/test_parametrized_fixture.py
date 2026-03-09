"""
示例3: 参数化fixture
对应 specs/需求.md 第332-352行的使用示例
"""
import pytest

from dynamic_params import with_dynamic_params
from tests.generators import generate_config


# 定义参数化fixture
@pytest.fixture(params=["dev", "test", "prod"])
def environment(request):
    """环境配置fixture"""
    return {"env": request.param, "timeout": 30}


class TestParametrizedFixture:
    """测试使用参数化fixture的测试类"""
    
    @with_dynamic_params(config=generate_config)
    @pytest.mark.parametrize("feature_flag", ["A/B", "control"])
    def test_parametrized_fixture(self, environment, feature_flag, config):
        """测试用例数量：3个环境 × 2个feature_flag = 6个"""
        assert config["env"] == environment["env"]
        assert config["feature"] == feature_flag
        assert config["timeout"] == environment["timeout"] + 10
