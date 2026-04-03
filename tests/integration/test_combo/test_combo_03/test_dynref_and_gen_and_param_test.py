"""
DynRef + param_generator + parametrize_test 组合测试

测试 DynRef、param_generator 和 parametrize_test 三者的组合使用

结论：DynRef 不能在模块级别运算，必须在测试内部预计算值
"""
import pytest
from dynamic_params import DynRef, param_generator, parametrize_test


# ============== 失败示例（不支持的组合） ==============

@param_generator
def gen_base_values():
    """生成基础值 - 模块级别使用"""
    return [1, 2, 3]


@parametrize_test("base", gen_base_values)
@parametrize_test("doubled", [DynRef("base") * 2])
def test_dynref_gen_param_test_uncollected(base, doubled):
    """测试三组件基础组合 - 原始版本（uncollected: DynRef 不能在模块级别运算）"""
    assert doubled == base * 2
