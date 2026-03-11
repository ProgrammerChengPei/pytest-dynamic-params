"""
高级用法示例

此文件包含pytest-dynamic-params插件的高级使用示例
"""

import pytest
import time

from dynamic_params import param_generator, with_dynamic_params


# 示例1：多个动态参数嵌套
@param_generator
def get_raw_data(data_source, size):
    """基础数据生成器"""
    return [{"id": i + 1, "source": data_source} for i in range(size)]


@param_generator
def process_data(raw_data, algorithm):
    """处理数据生成器，依赖于raw_data"""
    if algorithm == "algo1":
        return [{"id": item["id"], "processed": item["id"] * 2} for item in raw_data]
    else:
        return [{"id": item["id"], "processed": item["id"] * 3} for item in raw_data]


@param_generator
def validate_results(processed_data, threshold):
    """验证结果生成器，依赖于processed_data"""
    scores = [item["processed"] for item in processed_data]
    return all(score >= threshold for score in scores)


@with_dynamic_params(
    raw_data=get_raw_data,
    processed_data=process_data,
    is_valid=validate_results
)
@pytest.mark.parametrize("data_source", ["api", "database"])
@pytest.mark.parametrize("size", [5, 10])
@pytest.mark.parametrize("algorithm", ["algo1", "algo2"])
@pytest.mark.parametrize("threshold", [0.5, 8.0])
def test_dynamic_params_nesting(
    data_source, size, algorithm, threshold,
    raw_data, processed_data, is_valid
):
    """多个动态参数嵌套依赖测试示例"""
    # 验证原始数据
    assert len(raw_data) == size
    assert all(item["source"] == data_source for item in raw_data)
    
    # 验证处理后的数据
    assert len(processed_data) == size
    assert all(item["id"] == raw_item["id"] for item, raw_item in zip(processed_data, raw_data))
    
    # 验证结果
    assert isinstance(is_valid, bool)


# 示例2：作用域管理
@param_generator(scope="function")
def function_scoped_data(input_value):
    """函数作用域参数生成器"""
    return f"func_{input_value}"


@param_generator(scope="class")
def class_scoped_data():
    """类作用域参数生成器"""
    return "class_shared"


@param_generator(scope="module")
def module_scoped_data():
    """模块作用域参数生成器"""
    return "module_shared"


@param_generator(scope="session")
def session_scoped_data():
    """会话作用域参数生成器"""
    return "session_shared"


class TestScopesUsage:
    """作用域使用测试类示例"""
    
    @with_dynamic_params(
        func_data=function_scoped_data,
        class_data=class_scoped_data,
        mod_data=module_scoped_data,
        session_data=session_scoped_data
    )
    @pytest.mark.parametrize("input_value", [1, 2])
    def test_scope_management(self, input_value, func_data, class_data, mod_data, session_data):
        """作用域管理测试示例"""
        assert func_data == f"func_{input_value}"
        assert class_data == "class_shared"
        assert mod_data == "module_shared"
        assert session_data == "session_shared"


# 示例3：缓存控制
@param_generator(cache=True)
def cached_data(input_value):
    """启用缓存的参数生成器"""
    # 模拟计算密集型操作
    time.sleep(0.1)  # 模拟耗时操作
    return input_value * 10


@param_generator(cache=False)
def uncached_data():
    """禁用缓存的参数生成器"""
    # 每次调用返回不同值
    return time.time()


@with_dynamic_params(
    cached_result=cached_data,
    uncached_result=uncached_data
)
@pytest.mark.parametrize("input_value", [1, 2])
def test_cache_control(input_value, cached_result, uncached_result):
    """缓存控制测试示例"""
    # 验证缓存结果
    assert cached_result == input_value * 10
    
    # 验证非缓存结果（每次都不同）
    assert isinstance(uncached_result, float)


# 示例4：懒加载控制
@param_generator(lazy=True)
def lazy_data(input_value):
    """启用懒加载的参数生成器"""
    # 只有在实际使用时才会执行
    print(f"Lazy data generated for input: {input_value}")
    return input_value * 5


@param_generator(lazy=False)
def eager_data(input_value):
    """禁用懒加载的参数生成器"""
    # 会立即执行，不管是否使用
    print(f"Eager data generated for input: {input_value}")
    return input_value * 3


@with_dynamic_params(
    lazy_result=lazy_data,
    eager_result=eager_data
)
@pytest.mark.parametrize("input_value", [1, 2])
def test_lazy_loading(input_value, lazy_result, eager_result):
    """懒加载控制测试示例"""
    # 验证懒加载结果
    assert lazy_result == input_value * 5
    
    # 验证非懒加载结果
    assert eager_result == input_value * 3


# 示例5：组合配置（作用域 + 缓存 + 懒加载）
@param_generator(scope="module", cache=True, lazy=True)
def optimized_data(input_value):
    """优化配置的参数生成器"""
    # 模块级缓存 + 懒加载
    print(f"Optimized data generated for input: {input_value}")
    time.sleep(0.1)  # 模拟耗时操作
    return input_value * 100


@with_dynamic_params(optimized_result=optimized_data)
@pytest.mark.parametrize("input_value", [1, 2, 3])
def test_combined_config(input_value, optimized_result):
    """组合配置测试示例"""
    assert optimized_result == input_value * 100
