"""
param_generator 组件测试

测试 param_generator 装饰器组件的使用方式
可以配合任意 pytest 原生组件（fixture、pytest.mark.parametrize）
探索正确的使用方式，探索不支持的使用方式并给出替代方案。

结论：param_generator 必须在测试内部定义，不能在模块级别使用
"""

import pytest
from dynamic_params import param_generator, parametrize_test


def gen_yield():
    """基础参数生成器 - 模块级别使用"""
    for value in [1, 2, 3]:
        yield value


@pytest.mark.recommended
@pytest.mark.parametrize("value", gen_yield())
def test_dynamic_mark_param_yield(value):
    assert value in [1, 2, 3]


# 成功示例 01：@param_generator 可以被@pytest.mark.parametrize
# 失败示例 01: @pytest.mark.parametrize 不能动态参数化
@param_generator
def gen_basic():
    """基础参数生成器 - 模块级别使用"""
    for value in [1, 2, 3]:
        yield value


@pytest.fixture
def fix_value():
    """基础 fixture"""
    return 10


@pytest.mark.recommended
@pytest.mark.parametrize("value", gen_basic())
def test_dynamic_mark_param(value):
    assert value in [1, 2, 3]


# test_dynamic_mark_param 的推荐用法示例 01: @parametrize_test 可以动态参数化
@param_generator
def gen():
    for v in [1, 2, 3]:
        yield v


@pytest.mark.recommended
@parametrize_test("value", gen)
def test_plugin(value):
    assert value in [1, 2, 3]


# ============== 成功示例 ==============

# 成功示例 01：param_generator 支持动态计算参数（原生 pytest 无法实现）


@param_generator
def gen_squares():
    # 动态计算平方值，而不是预先存储
    for i in range(1, 6):
        yield i, i * i  # (输入，期望输出)


@pytest.mark.error
@pytest.mark.parametrize("num, square", gen_squares)
def test_pytest(num, square):
    assert num**2 == square


@pytest.mark.passed
@parametrize_test("num, square", gen_squares)
def test_self(num, square):
    assert num**2 == square


# 成功示例 02：param_generator 支持从外部数据源动态读取
@pytest.mark.collection_error
def test_gen_external_source():
    """测试 param_generator 从外部数据源动态读取（原生 pytest 需要预先加载所有数据）"""

    @param_generator
    def gen_from_data():
        # 模拟从文件/数据库动态读取数据
        data_source = ["apple", "banana", "cherry"]
        for item in data_source:
            yield item, len(item)

    @pytest.mark.parametrize("fruit, length", gen_from_data)
    def test(fruit, length):
        assert len(fruit) == length

    # 手动调用
    test("apple", 5)
    test("banana", 6)
    test("cherry", 6)
