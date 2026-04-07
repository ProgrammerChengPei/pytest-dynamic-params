"""
链式参数生成器演示 - 显式依赖模式

💡 专注插件功能：展示@pytest.mark.parametrize显式声明的链式依赖
🎯 核心特性：链式参数传递、显式依赖声明
"""

import pytest
from src.dynamic_params.public.decorators.param_generator import param_generator

# ========== 显式依赖模式示例 ==========

@param_generator(scope="session") 
def data_source():
    """基础数据源生成器 - session级别"""
    print("🔗 Fetching data from external source...")
    return [1, 2, 3, 4, 5]

@param_generator(scope="session")
def algorithm_list():
    """算法列表生成器 - session级别"""
    return ["linear", "quadratic", "exponential"]

@param_generator(scope="session")
@pytest.mark.parametrize("algorithm", algorithm_list)  # 💡 显式声明依赖
def processor(algorithm):
    """处理器生成器 - session级别"""
    print(f"🔗 Initializing processor for {algorithm}")
    processors = {
        "linear": lambda x: x * 2,
        "quadratic": lambda x: x ** 2,
        "exponential": lambda x: 2 ** x
    }
    return processors[algorithm]

@param_generator(scope="function")  
@pytest.mark.parametrize("data", data_source)  # 💡 显式声明依赖
@pytest.mark.parametrize("processor", processor)  # 💡 显式声明依赖
def process_data(data, processor):
    """链式数据处理生成器 - function级别"""
    print(f"🔗 Processing data={data} with processor")
    return {
        "input": data,
        "output": processor(data),
        "processor_type": str(processor)
    }

# ========== 多级链式示例 ==========

@param_generator(scope="session")
def multiplier_list():
    """乘数列表生成器 - session级别"""
    return [10, 20, 50]

@param_generator(scope="function")
@pytest.mark.parametrize("data", data_source)  # 💡 显式依赖session级生成器
@pytest.mark.parametrize("multiplier", multiplier_list)  # 💡 显式依赖session级生成器
def scaled_data(data, multiplier):
    """缩放数据处理生成器 - function级别"""
    return data * multiplier

@param_generator(scope="function")
@pytest.mark.parametrize("scaled", scaled_data)  # 💡 依赖function级生成器
@pytest.mark.parametrize("processor", processor)  # 💡 依赖session级生成器
def final_result(scaled, processor):
    """最终结果生成器 - function级别"""
    return processor(scaled)

# ========== 高级链式示例 ==========

@param_generator(scope="module")
def category_list():
    """数据分类生成器 - module级别"""
    return ["positive", "negative", "zero"]

@param_generator(scope="module")
@pytest.mark.parametrize("data", data_source)  # 💡 依赖session级
@pytest.mark.parametrize("category", category_list)  # 💡 依赖module级
def categorized_data(data, category):
    """分类数据处理生成器 - module级别"""
    if category == "positive":
        return abs(data)
    elif category == "negative":
        return -abs(data)
    else:  # zero
        return 0

# ========== 动态配置示例 ==========

@param_generator(scope="session")
def dynamic_config():
    """动态配置生成器 - session级别"""
    import random
    return {
        "factor": random.randint(1, 10),
        "offset": random.randint(0, 100)
    }

@param_generator(scope="function")
@pytest.mark.parametrize("config", dynamic_config)  # 💡 显式依赖
@pytest.mark.parametrize("data", data_source)  # 💡 显式依赖
def dynamically_calibrated(config, data):
    """动态校准数据生成器 - function级别"""
    return data * config["factor"] + config["offset"]

# ========== 插件功能测试 ==========

def test_plugin_features():
    """测试链式生成器插件功能"""
    
    # 测试基础生成器
    assert len(data_source()) == 5
    assert len(algorithm_list()) == 3
    
    # 测试链式生成器
    assert len(process_data()) == 5 * 3  # data × processors
    assert len(scaled_data()) == 5 * 3  # data × categories
    
    print("✅ 插件功能测试通过")

# ========== 演示链式调用 ==========

if __name__ == "__main__":
    print("🎯 链式生成器 - 显式依赖模式演示\n")
    
    print("🔗 数据源:", data_source())
    print("🔗 算法列表:", algorithm_list())
    print("🔗 处理器数量:", len(processor()))
    
    print("\n➡️ 链式生成结果:")
    results = process_data()
    print(f"  总测试用例数: {len(results)}")
    print(f"  单个结果示例: {results[0]}")
    
    print("\n➡️ 多级链式结果:")
    scaled_results = scaled_data()
    print(f"  缩放数据用例数: {len(scaled_results)}")
    
    final_results = final_result()
    print(f"  最终结果用例数: {len(final_results)}")
    
    print("\n✨ 显式依赖模式特色：")
    print("1. 明确依赖关系：通过@pytest.mark.parametrize清晰声明")
    print("2. 可定制化：支持不同级别的scope控制")
    print("3. 参数传递：链式参数在不同级别之间的传递")
    
    test_plugin_features()
    print("\n✅ 显式依赖模式演示完成！")