"""
测试懒加载功能
对应系统中的懒加载模式
"""

import pytest

from dynamic_params import dynamic_params, param_generator


@param_generator(lazy=True)
def lazy_generator(value):
    """懒加载生成器"""
    # 模拟耗时操作
    import time

    time.sleep(0.1)
    return value * 2


@param_generator(lazy=False)
def eager_generator(value):
    """非懒加载生成器"""
    # 模拟耗时操作
    import time

    time.sleep(0.1)
    return value * 2


class TestLazyLoading:
    """测试懒加载功能的测试类"""

    @dynamic_params(result=lazy_generator)
    @pytest.mark.parametrize("value", [2])
    def test_lazy_loading(self, value, result):
        """测试懒加载模式"""
        # 验证结果直接是计算值（插件会自动执行懒加载结果）
        assert result == 4

    @dynamic_params(result=eager_generator)
    @pytest.mark.parametrize("value", [2])
    def test_eager_loading(self, value, result):
        """测试非懒加载模式"""
        # 验证结果直接是计算值
        assert result == 4

    @dynamic_params(lazy_result=lazy_generator, eager_result=eager_generator)
    @pytest.mark.parametrize("value", [2])
    def test_mixed_loading(self, value, lazy_result, eager_result):
        """测试混合加载模式"""
        # 验证懒加载结果
        assert lazy_result == 4
        # 验证非懒加载结果
        assert eager_result == 4
