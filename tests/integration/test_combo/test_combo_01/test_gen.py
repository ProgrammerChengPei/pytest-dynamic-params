"""
param_generator 组件测试

测试 param_generator 装饰器组件的使用方式
可以配合 pytest 原生组件（fixture）

结论：param_generator 用于链式参数生成，支持在测试函数内部使用
"""

import pytest
from dynamic_params import param_generator


# 成功示例 01：简单的参数生成器测试
def test_simple_param_generator():
    """测试简单的 param_generator 用法"""
    
    @param_generator
    def basic_generator():
        """基础参数生成器"""
        for value in [1, 2, 3]:
            yield value
    
    assert list(basic_generator()) == [1, 2, 3]


# 成功示例 02：带参数的生成器测试
def test_param_generator_with_args():
    """测试带参数的 param_generator"""
    
    @param_generator
    def filtered_generator(max_value=5):
        """过滤生成器"""
        for value in range(1, max_value + 1):
            if value % 2 == 0:  # 只生成偶数
                yield value
    
    assert list(filtered_generator()) == [2, 4]
    assert list(filtered_generator(3)) == [2]


# 成功示例 03：param_generator 配合 pytest.parametrize - 仅作为数据源
def test_param_generator_as_data_source():
    """测试 param_generator 作为数据源配合 pytest.parametrize"""
    
    @param_generator
    def number_generator():
        """数字生成器"""
        for i in [10, 20, 30]:
            yield i
    
    # pytest.mark.parametrize 可以直接使用生成器输出
    @pytest.mark.parametrize("number", list(number_generator()))
    def test_numbers(number):
        assert number in [10, 20, 30]
    
    # 测试生成的数字
    assert list(number_generator()) == [10, 20, 30]


