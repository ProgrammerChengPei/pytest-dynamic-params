"""
parametrize_fixture 组件测试

测试 parametrize_fixture 装饰器组件的使用方式
可以配合任意 pytest 原生组件（fixture、pytest.mark.parametrize）
探索正确的使用方式，探索不支持的使用方式并给出替代方案。

结论：@parametrize_fixture 和 @pytest.fixture 不能同时应用到同一函数
"""
import pytest
from dynamic_params import parametrize_fixture


# 成功示例 01：parametrize_fixture 静态参数化 fixture
@parametrize_fixture("fix_basic", [1, 2, 3])
def fix_basic_impl(fix_basic):
    """基础参数化 fixture - 重复应用 fixture 装饰器"""
    return fix_basic

@pytest.mark.passed
def test_param_fix_with_fixture(fix_basic_impl):
    """测试 parametrize_fixture 与 fixture 组合"""
    assert fix_basic_impl in [1, 2, 3]


    
# 成功示例 02：parametrize_fixture 动态参数化 fixture
def gen_yield():
    """基础参数生成器 - 模块级别使用"""
    for value in [1, 2, 3]:
        yield value

@parametrize_fixture("fix_plugin", gen_yield)
def fix_plugin_impl(fix_plugin):
    """基础参数化 fixture - 使用生成器作为参数"""
    return fix_plugin * 2


def test_plugin(fix_plugin_impl):
    """测试 parametrize_fixture 与生成器组合，验证 fixture 处理后的值"""
    assert fix_plugin_impl in [2, 4, 6]  # fixture 处理后的值 (1*2, 2*2, 3*2)
    


# 成功示例 03：parametrize_fixture 支持多级 fixture


@parametrize_fixture("value", [100, 200, 300])
def get_fixture_params(value):
    return value

@pytest.fixture
def fix_impl(get_fixture_params):
    return get_fixture_params * 2  # 可以在 fixture 中进行处理


@pytest.mark.passed
def test_1(fix_impl):
    # assert fix_impl in [200, 400, 600]
    assert fix_impl in [200, 400, 600]
    



# 成功示例 04：parametrize_fixture 支持静态和动态混合的参数化 fixture

@parametrize_fixture("base", [10, 20])
def base_impl(base):
    return base

@parametrize_fixture("multiplier", gen_yield)
def mult_impl(multiplier):
    return multiplier


@pytest.mark.passed
def test_2(base_impl, mult_impl):
    print(f"base_impl={base_impl}, mult_impl={mult_impl}")
    result = base_impl * mult_impl
    assert result > 0
    