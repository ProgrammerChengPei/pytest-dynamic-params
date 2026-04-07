"""
param_generator 组件测试

测试 param_generator 装饰器组件的使用方式
可以配合任意 pytest 原生组件（fixture、pytest.mark.parametrize）
探索正确的使用方式，探索不支持的使用方式并给出替代方案。

结论：param_generator 必须在测试内部定义，不能在模块级别使用
"""

import pytest


def gen_yield():
    """基础参数生成器 - 模块级别使用"""
    for value in [1, 2, 3]:
        yield value


# 成功示例 01：@pytest.mark.parametrize 可以使用不带 @param_generator 的生成器
def gen_basic():
    """基础参数生成器 - 模块级别使用"""
    for value in [1, 2, 3]:
        yield value
        
@pytest.mark.parametrize("value", gen_basic())
def test_dynamic_mark_param(value):
    assert value in [1, 2, 3]


