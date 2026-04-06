"""
parametrize_test 组件测试

测试 parametrize_test 装饰器组件的使用方式
可以配合任意 pytest 原生组件（fixture、pytest.mark.parametrize）
探索正确的使用方式，探索不支持的使用方式并给出替代方案。

结论：fixture 可以在模块级别定义，parametrize_test 必须在测试内部使用
"""

import pytest
from dynamic_params import parametrize_test

# ============== 成功示例 ==============


# 成功示例 01：parametrize_test 参数化
def generate_test_cases():
    cases = []
    for i in range(1, 6):
        cases.append((i, i * 2))
    return cases


@pytest.mark.passed
@parametrize_test("num, doubled", generate_test_cases())
def test(num, doubled):
    assert num * 2 == doubled


# 成功示例 02：parametrize_test 支持多个参数化
def get_nums():
    return [10, 20, 30]


def get_multipliers():
    return [1, 2, 3]


@pytest.mark.passed
@parametrize_test("num", get_nums())
@parametrize_test("mult", get_multipliers())
def test_multi_parametrize(num, mult):
    result = num * mult
    assert result > 0


# 成功示例 03：parametrize_test 支持 fixture
@pytest.fixture
def fix_basic():
    """基础 fixture - 模块级别使用"""
    return [1, 2, 3]


@pytest.mark.passed
@parametrize_test("value", fix_basic)
def test_fixture(value):
    """测试 parametrize_test 与 fixture 组合"""
    assert value in [1, 2, 3]


# 成功示例 04：parametrize_test 支持动态 fixture
@pytest.fixture(params=[1, 2, 3])
def fix_dynamic(request):
    return request.param


@pytest.mark.passed
@parametrize_test("value", fix_dynamic)
def test_dynamic_fixture(value):
    assert value in [1, 2, 3]


# 成功示例 05：parametrize_test 支持多个 fixture （静态 fixture 和动态 fixture 混用）
@pytest.fixture
def fix_nums():
    return [10, 20, 30]


@pytest.fixture(params=[1, 2, 3])
def fix_multipliers(request):
    return request.param


@pytest.mark.passed
@parametrize_test("num", fix_nums)
@parametrize_test("mult", fix_multipliers)
def test_multi_fixture(num, mult):
    result = num * mult
    assert result > 0


# 成功示例 06：parametrize_test 支持与 pytest.mark.parametrize 混用
@pytest.mark.passed
@pytest.mark.parametrize("num", get_nums())
@parametrize_test("mult", get_multipliers())
def test_with_mark_parametrize(num, mult):
    result = num * mult
    assert result > 0
