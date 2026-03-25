"""
测试插件工具函数的单元测试
"""

from dynamic_params import dynamic_parametrize, generator, use_generators
from dynamic_params.plugin.utils import PluginUtils


class TestPluginUtils:
    """PluginUtils类的测试类"""

    def test_extract_dynamic_params(self):
        """测试提取动态参数映射"""
        # 测试没有动态参数的函数
        def test_func():
            pass
        
        result = PluginUtils.extract_dynamic_params(test_func)
        assert result == {}
        
        # 测试有动态参数的函数
        @generator
        def test_generator():
            return 42
        
        @use_generators(result=test_generator)
        def test_func_with_params():
            pass
        
        result = PluginUtils.extract_dynamic_params(test_func_with_params)
        assert "result" in result

    def test_is_dynamic_parametrized(self):
        """测试检查函数是否使用了 @dynamic_parametrize 装饰器"""
        # 测试没有使用 @dynamic_parametrize 的函数
        def test_func():
            pass
        
        result = PluginUtils.is_dynamic_parametrized(test_func)
        assert result is False
        
        # 测试使用了 @dynamic_parametrize 的函数
        @dynamic_parametrize("param", [1, 2, 3])
        def test_func_with_parametrize(param):
            pass
        
        result = PluginUtils.is_dynamic_parametrized(test_func_with_parametrize)
        assert result is True

    def test_is_use_generators(self):
        """测试检查函数是否使用了 @use_generators 装饰器"""
        # 测试没有使用 @use_generators 的函数
        def test_func():
            pass
        
        result = PluginUtils.is_use_generators(test_func)
        assert result is False
        
        # 测试使用了 @use_generators 的函数
        @generator
        def test_generator():
            return 42
        
        @use_generators(result=test_generator)
        def test_func_with_generators():
            pass
        
        result = PluginUtils.is_use_generators(test_func_with_generators)
        assert result is True

    def test_get_parametrize_info(self):
        """测试获取函数的参数化信息"""
        # 测试没有参数化信息的函数
        def test_func():
            pass
        
        result = PluginUtils.get_parametrize_info(test_func)
        assert result == []
        
        # 测试有参数化信息的函数
        @dynamic_parametrize("param", [1, 2, 3])
        def test_func_with_parametrize(param):
            pass
        
        result = PluginUtils.get_parametrize_info(test_func_with_parametrize)
        assert len(result) > 0

    def test_get_generator_mapping(self):
        """测试获取函数的生成器映射"""
        # 测试没有生成器映射的函数
        def test_func():
            pass
        
        result = PluginUtils.get_generator_mapping(test_func)
        assert result == {}
        
        # 测试有生成器映射的函数
        @generator
        def test_generator():
            return 42
        
        @use_generators(result=test_generator)
        def test_func_with_generators():
            pass
        
        result = PluginUtils.get_generator_mapping(test_func_with_generators)
        assert "result" in result
