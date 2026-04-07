import pytest


def gen_yield():
    """基础参数生成器 - 模块级别使用"""
    for value in [1, 2, 3]:
        yield value


@pytest.mark.skip_skip_collection_error(
    reason="@pytest.mark.parametrize 支持生成器对象，实际没有收集错误，不应该跳过"
)
@pytest.mark.passed(reason="@pytest.mark.parametrize 支持生成器对象")
@pytest.mark.parametrize("value", gen_yield())
def test_dynamic_mark_param_yield(value):
    assert value in [1, 2, 3]


##################################
@pytest.mark.skip_skip_collection_error(
    reason="@pytest.mark.parametrize 不支持函数对象，实际会产生收集错误，应该跳过"
)
@pytest.mark.parametrize("value", gen_yield)
def test_dynamic_mark_param_yield_func(value):
    assert value in [1, 2, 3]

##################################
@pytest.fixture
def fix_a():
    return "a"

@pytest.fixture
def fix_ab(fix_a):
    return fix_a + "b"

@pytest.mark.passed(
    reason="@pytest.mark.parametrize 支持 fixture 嵌套"
)
def test_ab(fix_ab):
    assert fix_ab == "ab"
