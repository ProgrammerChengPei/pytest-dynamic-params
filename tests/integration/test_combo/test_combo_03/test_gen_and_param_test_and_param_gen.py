"""
param_generator + parametrize_test + parametrize_generator 组合测试

测试 param_generator、parametrize_test 和 parametrize_generator 三者的组合使用

结论：@parametrize_generator 需要 (argnames, argvalues) 参数，应该使用 @param_generator 替代
"""
import pytest
from dynamic_params import param_generator, parametrize_test, parametrize_generator


# ============== 失败示例（不支持的组合） ==============

@parametrize_generator("base", [10, 20, 30])
def param_gen_base(base):
    """基础参数化生成器 - 模块级别使用"""
    yield base


@param_generator
def gen_multiplier():
    """生成乘数 - 模块级别使用"""
    return [1, 2, 3]


@parametrize_test("base", param_gen_base)
@parametrize_test("multiplier", gen_multiplier)
def test_gen_param_test_param_gen_uncollected(base, multiplier):
    """测试三组件基础组合 - 原始版本（uncollected: 用法不正确）"""
    assert base in [10, 20, 30]
    assert multiplier in [1, 2, 3]
