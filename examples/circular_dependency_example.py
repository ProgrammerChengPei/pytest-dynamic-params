"""
循环依赖检测使用示例

该示例演示了pytest-dynamic-params插件如何检测和报告循环依赖
"""

import pytest

from dynamic_params import param_generator, with_dynamic_params


# 示例1：正常的依赖关系（不会报错）
@param_generator
def generate_base_data():
    """基础数据生成器"""
    return {"id": 1, "name": "test"}


@param_generator
def generate_processed_data(base_data):
    """处理后的数据生成器，依赖于基础数据"""
    return {**base_data, "processed": True, "extra_field": "value"}


@with_dynamic_params(
    base_data=generate_base_data,
    processed_data=generate_processed_data
)
@pytest.mark.parametrize("test_case", ["normal"])
def test_normal_dependency_example(test_case, base_data, processed_data):
    """正常依赖关系的测试示例"""
    assert processed_data["id"] == base_data["id"]
    assert processed_data["processed"] is True


# 示例2：循环依赖（会导致错误）
# 这段代码演示了循环依赖的情况，如果您取消注释并运行，
# 将会收到 CircularDependencyError 异常
"""
@param_generator
def generate_a(b_value):
    '''生成器A依赖于B'''
    return f"A_based_on_{b_value}"

@param_generator 
def generate_b(a_value):
    '''生成器B依赖于A - 这将导致循环依赖'''
    return f"B_based_on_{a_value}"

@with_dynamic_params(
    a=generate_a,
    b=generate_b
)
def test_circular_dependency_example(a, b):
    '''这个测试会因为循环依赖而失败'''
    pass
"""


def demonstrate_circular_dependency():
    """
    如何演示循环依赖错误：
    
    1. 取消注释上面被注释的代码块
    2. 运行测试，将看到类似以下的错误：
    
    CircularDependencyError: 检测到循环依赖: generate_a -> generate_b -> generate_a
    """
    print("这是一个演示循环依赖错误的示例")
    print("如果您想看到循环依赖错误，请取消注释代码中的相关部分")


if __name__ == "__main__":
    demonstrate_circular_dependency()