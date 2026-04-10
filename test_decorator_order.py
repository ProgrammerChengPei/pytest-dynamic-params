#!/usr/bin/env python3
"""
测试装饰器自动顺序调整功能
"""

import pytest
from dynamic_params.public.decorators.param_generator import param_generator, _detect_decorator_order


def test_detector_order_detection():
    """测试装饰器顺序检测功能"""
    
    # 测试用例1：正确的顺序
    correct_source = '''
@pytest.mark.parametrize("arg", [1, 2, 3])
@param_generator
def my_generator(arg):
    yield arg
'''
    result = _detect_decorator_order(correct_source)
    assert result['order'] == ['parametrize', 'param_generator']
    assert result['is_correct_order'] == True
    
    # 测试用例2：错误的顺序
    wrong_source = '''
@param_generator
@pytest.mark.parametrize("arg", [1, 2, 3])
def my_generator(arg):
    yield arg
'''
    result = _detect_decorator_order(wrong_source)
    assert result['order'] == ['param_generator', 'parametrize']
    assert result['is_correct_order'] == False
    
    # 测试用例3：只有param_generator
    only_pg_source = '''
@param_generator
def my_generator():
    yield "data"
'''
    result = _detect_decorator_order(only_pg_source)
    assert result['order'] == ['param_generator']
    assert result['is_correct_order'] == True
    
    print("✅ 装饰器顺序检测测试通过")


def test_manual_decorator_application():
    """手动应用装饰器测试顺序调整"""
    
    # 测试正确的顺序
    @pytest.mark.parametrize("value", [1, 2, 3])
    @param_generator
    def correct_order_generator(value):
        """正确顺序的生成器"""
        yield f"data_{value}", value
    
    assert hasattr(correct_order_generator, '_param_generator_called')
    assert correct_order_generator.__name__ == "correct_order_generator"
    
    print("✅ 手动装饰器应用测试通过")


if __name__ == "__main__":
    test_detector_order_detection()
    test_manual_decorator_application()
    print("🎉 所有装饰器顺序调整测试通过！")