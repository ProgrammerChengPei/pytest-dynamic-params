"""
测试错误处理
对应需求文档中关于错误提示的部分
"""
import pytest

from dynamic_params import with_dynamic_params


# 定义一个未使用@param_generator装饰的函数
def unmarked_generator(input_value):
    """未标记的生成器函数"""
    return input_value * 2


class TestErrorHandling:
    """测试错误处理的测试类"""
    
    def test_unmarked_generator_error(self):
        """测试使用未标记生成器时的错误"""
        # 使用上下文管理器捕获异常
        with pytest.raises(ValueError) as exc_info:
            @with_dynamic_params(result=unmarked_generator)
            def dummy_test():
                pass
        
        # 验证错误消息包含预期内容
        assert "@param_generator" in str(exc_info.value)
        assert "decorated" in str(exc_info.value).lower()