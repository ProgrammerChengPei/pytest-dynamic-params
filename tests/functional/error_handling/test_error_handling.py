"""
测试错误处理
对应需求文档中关于错误提示的部分
"""

import pytest

from dynamic_params import param_generator, with_dynamic_params
from tests.utils import assert_error_message, failing_generator


# 定义一个未使用@param_generator装饰的函数
def unmarked_generator(input_value):
    """未标记的生成器函数"""
    return input_value * 2


# 定义需要缺失参数的生成器
@param_generator
def requires_missing_param(missing_param):
    """需要缺失参数的生成器"""
    return missing_param


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
        assert_error_message(exc_info, "@param_generator")
        assert "decorated" in str(exc_info.value).lower()

    @with_dynamic_params(result=requires_missing_param)
    def test_missing_param_error(self, result):
        """测试参数缺失错误"""
        # 由于系统会在参数生成时处理错误，我们期望result为None
        assert result is None

    @with_dynamic_params(result=failing_generator)
    def test_generator_execution_error(self, result):
        """测试生成器执行错误"""
        # 由于系统会在参数生成时处理错误，我们期望result为None
        assert result is None
