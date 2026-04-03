"""
param_generator + parametrize_test + parametrize_fixture 组合测试

测试 param_generator、parametrize_test 和 parametrize_fixture 三者的组合使用

结论：@parametrize_fixture 和 @pytest.fixture 不能同时应用到同一函数
"""
import pytest
from dynamic_params import param_generator, parametrize_test, parametrize_fixture


# ============== 失败示例（不支持的组合） ==============

@parametrize_fixture("fix_base", [10, 20, 30])
@pytest.fixture(scope="function")
def fix_base_impl(fix_base):
    """基础参数化 fixture - 重复应用 fixture 装饰器"""
    return fix_base


@param_generator
def gen_multiplier():
    """生成乘数 - 模块级别使用"""
    return [1, 2, 3]


@parametrize_test("base", fix_base_impl)
@parametrize_test("multiplier", gen_multiplier)
def test_gen_param_test_param_fix_uncollected(base, multiplier):
    """测试三组件基础组合 - 原始版本（uncollected: fixture 重复应用）"""
    assert base in [10, 20, 30]
    assert multiplier in [1, 2, 3]
