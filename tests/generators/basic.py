"""基础参数生成器"""

from dynamic_params import param_generator


@param_generator
def calculate_result(input_value):
    """计算结果 - 最简单的参数生成器"""
    return input_value * 2
