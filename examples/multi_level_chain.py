"""
真正的多级链式参数生成器演示 - A → B → C 依赖链

🎯 核心概念：
- 生成器C的某个参数依赖生成器B
- 生成器B的某个参数依赖生成器A  
- 形成 A → B → C 的链式依赖结构
"""

import pytest
from src.dynamic_params.public.decorators.param_generator import param_generator

# ========== 第一级：基础数据源生成器 ==========

@param_generator(scope="session") 
def raw_data_source():
    """第一级：原始数据源生成器"""
    print("🔗 1级: 获取原始数据源...")
    return [10, 20, 30, 40, 50]

@param_generator(scope="session")
def operation_type():
    """第一级：操作类型生成器"""
    return ["scale", "offset", "invert"]

# ========== 第二级：中间处理生成器 ==========

@param_generator
@pytest.mark.parametrize("data", raw_data_source)  # 💡 依赖第一级
def data_validator(data):
    """第二级：数据验证器 - 依赖 raw_data_source"""
    print(f"🔗 2级: 验证数据 {data}")
    # 简单的验证逻辑
    if data > 0:
        return {"original": data, "validated": True, "factor": 2}
    else:
        return {"original": data, "validated": False, "factor": 1}

@param_generator
@pytest.mark.parametrize("operation", operation_type)  # 💡 依赖第一级
def operation_configurator(operation):
    """第二级：操作配置器 - 依赖 operation_type"""
    print(f"🔗 2级: 配置操作 {operation}")
    configs = {
        "scale": {"type": "scale", "multiplier": 3},
        "offset": {"type": "offset", "adjustment": 100}, 
        "invert": {"type": "invert", "divisor": 2}
    }
    return configs[operation]

# ========== 第三级：最终处理生成器 ==========

@param_generator
@pytest.mark.parametrize("validated_data", data_validator)  # 💡 依赖第二级
@pytest.mark.parametrize("operation_config", operation_configurator)  # 💡 依赖第二级
def data_processor(validated_data, operation_config):
    """第三级：数据处理器 - 依赖第二级的两个生成器"""
    print(f"🔗 3级: 处理数据 {validated_data} with {operation_config}")
    
    if not validated_data["validated"]:
        return {"result": 0, "status": "invalid"}
    
    # 根据操作配置处理数据
    op_type = operation_config["type"]
    if op_type == "scale":
        result = validated_data["original"] * operation_config["multiplier"]
    elif op_type == "offset":
        result = validated_data["original"] + operation_config["adjustment"]
    else:  # invert
        result = validated_data["original"] / operation_config["divisor"]
    
    return {
        "original": validated_data["original"],
        "operation": op_type,
        "result": result,
        "level": 3
    }

# ========== 第四级：复杂业务逻辑生成器 ==========

@param_generator
@pytest.mark.parametrize("processed_data", data_processor)  # 💡 依赖第三级
def business_logic_executor(processed_data):
    """第四级：业务逻辑执行器 - 依赖第三级生成器"""
    print(f"🔗 4级: 执行业务逻辑 {processed_data}")
    
    # 更复杂的业务逻辑
    result = processed_data["result"]
    if result > 100:
        business_result = "High"
    elif result > 50:
        business_result = "Medium" 
    else:
        business_result = "Low"
    
    return {
        **processed_data,
        "business_result": business_result,
        "final_metric": result * 1.1,
        "level": 4
    }

# ========== 五级链式：超复杂场景 ==========

@param_generator(scope="module")
def quality_threshold():
    """第五级：质量阈值生成器"""
    return [50, 100, 150]

@param_generator
@pytest.mark.parametrize("final_result", business_logic_executor)  # 💡 依赖第四级
@pytest.mark.parametrize("threshold", quality_threshold)  # 💡 依赖第五级的独立生成器
def quality_assessor(final_result, threshold):
    """第五级：质量评估器 - 形成最大依赖链"""
    print(f"🔗 5级: 评估质量 {final_result} against {threshold}")
    
    passes_threshold = final_result["final_metric"] > threshold
    
    return {
        **final_result,
        "quality_threshold": threshold,
        "passes": passes_threshold,
        "assessment": "Good" if passes_threshold else "Needs Improvement",
        "level": 5
    }

# ========== 依赖链可视化演示 ==========

def test_multi_level_chain():
    """测试多级链式依赖结构"""
    
    print("\n🎯 多级依赖链结构：")
    print("raw_data_source (1级) → data_validator (2级)")
    print("operation_type (1级) → operation_configurator (2级)")
    print("data_validator (2级) + operation_configurator (2级) → data_processor (3级)")
    print("data_processor (3级) → business_logic_executor (4级)")
    print("business_logic_executor (4级) + quality_threshold (5级) → quality_assessor (5级)")
    
    # 测试各级生成器
    print(f"\n📊 各级生成器用例数：")
    print(f"   第1级 - raw_data_source: {len(raw_data_source())}")
    print(f"   第1级 - operation_type: {len(operation_type())}")
    print(f"   第2级 - data_validator: {len(data_validator())}")
    print(f"   第2级 - operation_configurator: {len(operation_configurator())}")
    print(f"   第3级 - data_processor: {len(data_processor())}")
    print(f"   第4级 - business_logic_executor: {len(business_logic_executor())}")
    print(f"   第5级 - quality_assessor: {len(quality_assessor())}")
    
    # 计算总测试用例数
    total_cases = len(quality_assessor())
    expected_cases = len(raw_data_source()) * len(operation_type()) * len(quality_threshold())
    
    print(f"\n🧮 链式组合计算：")
    print(f"   原始数据源数: {len(raw_data_source())}")
    print(f"   操作类型数: {len(operation_type())}")
    print(f"   质量阈值数: {len(quality_threshold())}")
    print(f"   理论组合数: {expected_cases}")
    print(f"   实际生成数: {total_cases}")
    
    assert total_cases == expected_cases, f"用例数不匹配: {total_cases} vs {expected_cases}"

# ========== 特定路径测试 ==========

@pytest.mark.parametrize("result", data_processor)
def test_level_3_chains(result):
    """测试第3级链式生成器"""
    assert "result" in result
    assert "level" in result and result["level"] == 3

@pytest.mark.parametrize("result", business_logic_executor)  
def test_level_4_chains(result):
    """测试第4级链式生成器"""
    assert "business_result" in result
    assert "level" in result and result["level"] == 4

@pytest.mark.parametrize("result", quality_assessor)
def test_level_5_chains(result):
    """测试第5级链式生成器"""
    assert "assessment" in result
    assert "level" in result and result["level"] == 5

# ========== 演示执行 ==========

if __name__ == "__main__":
    print("🚀 真实多级链式生成器演示\n")
    
    test_multi_level_chain()
    
    print("\n✨ 多级链式核心特性：")
    print("1. 真正的依赖链：A → B → C 清晰的层级关系")
    print("2. 分支合并：多路径可以汇聚到单一生成器")
    print("3. 独立层级：每级可以有独立scope设置")
    print("4. 组合爆炸：正确计算各级参数的交叉组合")
    
    # 展示结果示例
    print("\n🔍 第五级生成结果示例：")
    results = quality_assessor()
    for i, result in enumerate(results[:3]):  # 显示前3个
        print(f"   {i+1}. {result}")
    
    print(f"\n✅ 多级链式功能验证完成！总用例数: {len(results)}")