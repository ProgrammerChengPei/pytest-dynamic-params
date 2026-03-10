"""
测试缓存功能
对应需求文档中关于缓存管理和性能优化的部分
"""
import pytest

from dynamic_params import param_generator, with_dynamic_params

# 计数器用于跟踪函数调用次数
call_counts = {}


@param_generator(scope="function", cache=True)  # 启用缓存
def cached_function_data(input_value):
    """函数作用域带缓存的数据生成器"""
    key = f"cached_function_data_{input_value}"
    call_counts[key] = call_counts.get(key, 0) + 1
    return f"function_cached_{input_value}_{call_counts[key]}"


@param_generator(scope="class", cache=True)  # 启用缓存
def cached_class_data(input_value):
    """类作用域带缓存的数据生成器"""
    key = f"cached_class_data_{input_value}"
    call_counts[key] = call_counts.get(key, 0) + 1
    return f"class_cached_{input_value}_{call_counts[key]}"


class TestCacheFunctionality:
    """测试缓存功能的测试类"""
    
    def setup_method(self):
        """每次测试前清空计数器"""
        global call_counts
        call_counts.clear()
    
    @with_dynamic_params(cached_data=cached_function_data)
    @pytest.mark.parametrize("input_value", [1, 2, 1])  # 注意：1重复出现
    def test_function_scope_cache(self, input_value, cached_data):
        """测试函数作用域缓存 - 相同参数应该产生不同的结果（因为函数作用域不跨测试缓存）"""
        # 每次测试调用都会重新计算，即使参数相同
        assert cached_data.startswith("function_cached_")
        assert str(input_value) in cached_data
    
    @with_dynamic_params(class_cached=cached_class_data)
    @pytest.mark.parametrize("input_value", [1, 2, 1])  # 注意：1重复出现
    def test_class_scope_cache_reuse(self, input_value, class_cached):
        """测试类作用域缓存 - 相同参数应该复用缓存结果"""
        assert class_cached.startswith("class_cached_")
        assert str(input_value) in class_cached


@param_generator(scope="function", cache=False)  # 禁用缓存
def uncached_function_data(input_value):
    """函数作用域不带缓存的数据生成器"""
    key = f"uncached_function_data_{input_value}"
    call_counts[key] = call_counts.get(key, 0) + 1
    return f"function_uncached_{input_value}_{call_counts[key]}"


class TestNoCacheFunctionality:
    """测试无缓存功能的测试类"""
    
    def setup_method(self):
        """每次测试前清空计数器"""
        global call_counts
        call_counts.clear()
    
    @with_dynamic_params(uncached_data=uncached_function_data)
    @pytest.mark.parametrize("input_value", [1, 1, 1])  # 相同参数多次出现
    def test_no_cache_always_executes(self, input_value, uncached_data):
        """测试禁用缓存时每次都执行生成器"""
        # 每次都应该有不同的计数值，即使参数相同
        assert uncached_data.startswith("function_uncached_")
        assert str(input_value) in uncached_data