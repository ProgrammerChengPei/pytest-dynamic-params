"""
链式生成器重构示例
使用链式生成器替代复杂的DynRef和parametrize_test
"""

import pytest
from dynamic_params import param_generator

# ========== 重构示例1：数据处理管道（原多级依赖） ==========

@param_generator(scope="function")
def base_data_source(data_source, size):
    """基础数据生成器 - 替换原get_raw_data"""
    import random
    import time
    
    data = []
    for i in range(size):
        item = {
            "id": i + 1,
            "source": data_source,
            "value": random.randint(1, 100),
            "timestamp": time.time(),
        }
        data.append(item)
    return data

@param_generator(dependencies=["base_data_source"])
def process_data(base_data_source):
    """数据处理 - 替换原process_data，通过依赖传递"""
    processed_data = []
    algorithm = "algo1"  # 简化为固定算法，实际可以从参数传入
    
    for item in base_data_source:
        if algorithm == "algo1":
            processed_value = item["value"] ** 2
        else:
            processed_value = item["value"]
            
        processed_item = {
            "id": item["id"],
            "source": item["source"],
            "original_value": item["value"],
            "processed": processed_value,
            "algorithm": algorithm,
        }
        processed_data.append(processed_item)
    return processed_data

@pytest.mark.parametrize("data_source", ["api", "database", "file"])
@pytest.mark.parametrize("size", [5, 10])
def test_data_processing_chain(data_source, size):
    """测试数据处理的链式生成器"""
    raw_data = base_data_source(data_source, size)
    processed = process_data()
    
    # 验证原始数据
    assert len(raw_data) == size
    assert all(item["source"] == data_source for item in raw_data)
    
    # 验证处理后的数据
    assert len(processed) == size
    assert all(item["algorithm"] == "algo1" for item in processed)

# ========== 重构示例2：替换复杂DynRef表达式 ==========

# 原示例：DynRef("base") * DynRef("multiplier") 的链式生成器替换

@param_generator
def base_values():
    """基础值 - 替换原DynRef("base")"""
    return [2, 3, 5]

@param_generator
def multiplier_values():
    """乘数值 - 替换原DynRef("multiplier")"""
    return [10, 20, 30]

@param_generator(dependencies=["base_values", "multiplier_values"])
def combined_calculation(base_values, multiplier_values):
    """组合计算 - 替换DynRef表达式"""
    results = []
    for base in base_values:
        for mult in multiplier_values:
            results.append(base * mult)
    return results

@pytest.mark.parametrize("result", combined_calculation)
def test_combined_calculation_replacement(result):
    """测试组合计算（替换DynRef表达式）"""
    expected = [2*10, 2*20, 2*30, 3*10, 3*20, 3*30, 5*10, 5*20, 5*30]
    assert result in expected

# ========== 重构示例3：动态依赖关系 ==========

@param_generator(scope="function", cache=False)
def dynamic_input():
    """动态输入源"""
    import random
    return [random.randint(1, 10) for _ in range(3)]

@param_generator(dependencies=["dynamic_input"])
def process_dynamic(dynamic_input):
    """处理动态数据"""
    return [x * 10 for x in dynamic_input]

@param_generator(dependencies=["process_dynamic"])
def validate_dynamic(process_dynamic):
    """验证动态处理结果"""
    return [{"value": x, "valid": x > 50} for x in process_dynamic]

@pytest.mark.parametrize("result", validate_dynamic)
def test_dynamic_chain(result):
    """测试动态依赖链"""
    assert "value" in result
    assert "valid" in result
    assert result["value"] % 10 == 0

# ========== 重构示例4：配置组合 ==========

@param_generator(scope="session")
def global_config():
    """全局配置"""
    return {
        "api_url": "http://localhost:8000",
        "timeout": 30,
        "api_key": "test-key"
    }

@param_generator(dependencies=["global_config"])
def service_endpoints(global_config):
    """服务端点 - 基于全局配置"""
    return {
        "auth": f"{global_config['api_url']}/auth",
        "users": f"{global_config['api_url']}/users",
        "products": f"{global_config['api_url']}/products"
    }

@pytest.mark.parametrize("service", ["auth", "users", "products"])
def test_service_configuration(service):
    """测试服务配置"""
    endpoints = service_endpoints()
    assert service in endpoints
    assert endpoints[service].startswith("http")

# ========== 重构示例5：条件处理链 ==========

@param_generator
def input_scenarios():
    """输入场景"""
    return [
        {"type": "normal", "value": 10},
        {"type": "edge", "value": 0},
        {"type": "large", "value": 100}
    ]

@param_generator(dependencies=["input_scenarios"])
def conditional_processing(input_scenarios):
    """条件处理"""
    results = []
    for scenario in input_scenarios:
        if scenario["type"] == "normal":
            result = scenario["value"] * 2
        elif scenario["type"] == "edge":
            result = scenario["value"] + 1  # 边界情况处理
        else:  # large
            result = scenario["value"] // 2
        results.append({
            "scenario": scenario,
            "result": result,
            "processed": True
        })
    return results

@pytest.mark.parametrize("processed", conditional_processing)
def test_conditional_processing(processed):
    """测试条件处理链"""
    scenario = processed["scenario"]
    result = processed["result"]
    
    if scenario["type"] == "normal":
        assert result == scenario["value"] * 2
    elif scenario["type"] == "edge":
        assert result == scenario["value"] + 1
    elif scenario["type"] == "large":
        assert result == scenario["value"] // 2

# ========== 重构优势总结 ==========

"""
链式生成器重构的优势：

1. 代码清晰：通过函数参数显式声明依赖关系，比DynRef更直观
2. 易于调试：传统的函数调用栈比复杂的DynRef解析更容易调试
3. 与pytest兼容：完全兼容原生pytest.mark.parametrize
4. 简化架构：不需要复杂的DynRef和parametrize_test实现
5. 性能提升：避免了运行时的动态引用解析开销

重构的核心原则：
- 将DynRef("A") * DynRef("B")这样的复杂表达式
- 替换为@param_generator(dependencies=["A", "B"]) def calc(A, B)
- 然后使用@pytest.mark.parametrize("result", calc)
