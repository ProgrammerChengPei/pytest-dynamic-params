"""
DynRef + param_generator + parametrize_test + parametrize_fixture 组合测试

测试四个组件的组合使用

结论：@parametrize_fixture 和 @pytest.fixture 不能同时应用，DynRef 不能在模块级别运算
"""
import pytest
from dynamic_params import (
    DynRef,
    param_generator,
    parametrize_fixture,
    parametrize_test,
)


# ============== 失败示例（不支持的组合） ==============

@parametrize_fixture("fix_base", [1, 2, 3])
@pytest.fixture(scope="function")
def fix_base_impl(fix_base):
    """基础参数化 fixture - 重复应用 fixture 装饰器"""
    return fix_base


@param_generator
def gen_multiplier():
    """生成乘数 - 模块级别使用"""
    return [2, 3, 4]


@parametrize_test("base", fix_base_impl)
@parametrize_test("multiplier", gen_multiplier)
@parametrize_test("result", [DynRef("base") * DynRef("multiplier")])
def test_four_components_uncollected(base, multiplier, result):
    """测试四组件基础组合 - 原始版本（uncollected: fixture 重复应用 + DynRef 模块级运算）"""
    assert result == base * multiplier
