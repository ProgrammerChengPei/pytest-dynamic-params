"""
DynRef + param_generator + parametrize_test + parametrize_generator 组合测试

测试四个组件的组合使用

结论：@parametrize_generator 用法不正确，DynRef 不能在模块级别运算
"""
import pytest
from dynamic_params import (
    DynRef,
    param_generator,
    parametrize_generator,
    parametrize_test,
)


# ============== 失败示例（不支持的组合） ==============

@parametrize_generator("base", [1, 2, 3])
def param_gen_base(base):
    """基础参数化生成器 - 模块级别使用"""
    yield base


@param_generator
def gen_multiplier():
    """生成乘数 - 模块级别使用"""
    return [2, 3, 4]


@parametrize_test("base", param_gen_base)
@parametrize_test("multiplier", gen_multiplier)
@parametrize_test("result", [DynRef("base") * DynRef("multiplier")])
def test_four_components_uncollected(base, multiplier, result):
    """测试四组件基础组合 - 原始版本（uncollected: 用法不正确 + DynRef 模块级运算）"""
    assert result == base * multiplier
