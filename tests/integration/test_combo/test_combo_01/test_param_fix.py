"""
parametrize_fixture 组件测试

测试 parametrize_fixture 装饰器组件的使用方式
可以配合 pytest 原生组件（fixture）

结论：@parametrize_fixture 支持静态参数化fixture
"""
import pytest
from dynamic_params import parametrize_fixture


# 成功示例 01：parametrize_fixture 静态参数化 fixture
@parametrize_fixture("fix_basic", [1, 2, 3])
def fix_basic_impl(fix_basic):
    """基础参数化 fixture"""
    return fix_basic

@pytest.mark.passed
def test_param_fix_with_fixture(fix_basic_impl):
    """测试 parametrize_fixture 与 fixture 组合"""
    assert fix_basic_impl in [1, 2, 3]


# 成功示例 02：parametrize_fixture 支持多级 fixture
@parametrize_fixture("value", [100, 200, 300])
def get_fixture_params(value):
    return value

@pytest.fixture
def fix_impl(get_fixture_params):
    return get_fixture_params * 2  # 可以在 fixture 中进行处理


@pytest.mark.passed
def test_param_fix_multilayer(fix_impl):
    """测试 parametrize_fixture 的多层 fixture 组合"""
    assert fix_impl in [200, 400, 600]


# 成功示例 03：parametrize_fixture 支持静态混合参数化
@parametrize_fixture("base", [10, 20])
def base_impl(base):
    return base

@parametrize_fixture("multiplier", [1, 2, 3])
def mult_impl(multiplier):
    return multiplier


@pytest.mark.passed
def test_param_fix_static_combination(base_impl, mult_impl):
    """测试 parametrize_fixture 的静态参数组合"""
    print(f"base_impl={base_impl}, mult_impl={mult_impl}")
    result = base_impl * mult_impl
    assert result > 0
    

# 成功示例 04：与 pytest.mark.parametrize 配合使用
def test_param_fix_with_parametrize():
    """测试 parametrize_fixture 与 pytest.mark.parametrize 的配合"""
    
    # 在函数内部定义 parametrize_fixture
    @parametrize_fixture("user_type", ["admin", "user", "guest"])
    def user_fixture(user_type):
        return user_type
    
    # 配合 pytest.mark.parametrize
    @pytest.mark.parametrize("action", ["read", "write"])
    def test_combined(user_fixture, action):
        """组合测试"""
        assert user_fixture in ["admin", "user", "guest"]
        assert action in ["read", "write"]
    