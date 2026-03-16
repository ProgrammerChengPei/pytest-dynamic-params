"""
测试断言工具函数
"""


def assert_error_message(error, expected_message):
    """断言错误消息包含预期内容"""
    assert expected_message in str(error.value)


def assert_cached_value(result, expected_value):
    """断言缓存值"""
    assert result == expected_value


def assert_lazy_result(result, expected_value):
    """断言懒加载结果"""
    assert hasattr(result, "__call__")
    assert result() == expected_value
