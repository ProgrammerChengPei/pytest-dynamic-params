"""
param_generator + parametrize_test + parametrize_generator + parametrize_fixture + DynRef 组合测试

测试五个核心组件的组合使用

结论：多个组件用法不正确，不支持此组合
"""
import pytest
from dynamic_params import (
    DynRef,
    param_generator,
    parametrize_fixture,
    parametrize_generator,
    parametrize_test,
)


# ============== 失败示例（不支持的组合） ==============

@parametrize_fixture("fix_base", [10, 20, 30])
@pytest.fixture(scope="function")
def fix_base_impl(fix_base):
    """基础参数化 fixture - 重复应用 fixture 装饰器"""
    return fix_base


@parametrize_generator("multiplier", [1, 2, 3])
def param_gen_multiplier(multiplier):
    """乘数参数化生成器 - 模块级别使用"""
    yield multiplier


@param_generator
def gen_offset():
    """生成偏移量 - 模块级别使用"""
    return [0, 5, 10]


@parametrize_test("base", fix_base_impl)
@parametrize_test("multiplier", param_gen_multiplier)
@parametrize_test("offset", gen_offset)
@parametrize_test("result", [DynRef("base") * DynRef("multiplier") + DynRef("offset")])
def test_five_components_uncollected(base, multiplier, offset, result):
    """测试五组件基础组合 - 原始版本（uncollected: 多个组件用法不正确）"""
    assert base in [10, 20, 30]
    assert multiplier in [1, 2, 3]
    assert offset in [0, 5, 10]
    assert result == base * multiplier + offset
