"""
真实多级链式参数生成器演示 - A → B → C 依赖链结构

🎯 核心概念：真实的A → B → C多级依赖链结构
"""

import pytest
from src.dynamic_params.public.decorators.param_generator import param_generator

# ========== 第1级：最基础的数据源 ==========

@param_generator(scope="session") 
def base_numbers():
    """第1级：基础数字生成器"""
    return list(range(1, 6))  # [1, 2, 3, 4, 5]

@param_generator(scope="session")
def operation_codes():
    """第1级：操作代码生成器"""
    return ['A', 'B', 'C']

# ========== 第2级：基于第1级的生成器 ==========

@param_generator
@pytest.mark.parametrize("number", base_numbers)  # 💡 依赖第1级
def squared_numbers(number):
    """第2级：平方数生成器 - 依赖base_numbers"""
    return {
        "original": number,
        "squared": number ** 2,
        "level": 2
    }

@param_generator
@pytest.mark.parametrize("code", operation_codes)  # 💡 依赖第1级  
def operation_configs(code):
    """第2级：操作配置生成器 - 依赖operation_codes"""
    configs = {
        'A': {'multiplier': 10},
        'B': {'multiplier': 20},
        'C': {'multiplier': 30}
    }
    return {"code": code, **configs[code], "level": 2}

# ========== 第3级：基于第2级的生成器 ==========

@param_generator
@pytest.mark.parametrize("squared_data", squared_numbers)  # 💡 依赖第2级
@pytest.mark.parametrize("config", operation_configs)  # 💡 依赖第2级
def processed_results(squared_data, config):
    """第3级：处理结果生成器 - 依赖第2级的两个生成器"""
    result = squared_data["squared"] * config["multiplier"]
    return {
        "chain": f"{squared_data['original']} → {squared_data['squared']} → {result}",
        "original": squared_data["original"],
        "squared": squared_data["squared"],
        "multiplier": config["multiplier"],
        "final": result,
        "level": 3
    }

# ========== 第4级：基于第3级的生成器 ==========

@param_generator(scope="module")
def threshold_levels():
    """第4级：阈值级别生成器（独立）"""
    return [100, 500, 1000]

@param_generator  
@pytest.mark.parametrize("result", processed_results)  # 💡 依赖第3级
@pytest.mark.parametrize("threshold", threshold_levels)  # 💡 依赖第4级独立生成器
def quality_assessment(result, threshold):
    """第4级：质量评估生成器 - 依赖第3级，形成完整依赖链"""
    passes = result["final"] > threshold
    return {
        **result,
        "threshold": threshold,
        "assessment": "PASS" if passes else "FAIL",
        "chain": f"{result['original']} → {result['squared']} → {result['final']} → {'PASS' if passes else 'FAIL'}",
        "level": 4
    }

# ========== 创建更长的依赖链：A → B → C → D → E ==========

@param_generator
@pytest.mark.parametrize("assessment", quality_assessment)  # 💡 依赖第4级
def final_report(assessment):
    """第5级：最终报告生成器 - 依赖第4级，形成5级依赖链"""
    return {
        "full_chain": assessment["chain"],
        "original_number": assessment["original"],
        "final_result": assessment["final"],
        "quality": assessment["assessment"],
        "level": 5
    }

# ========== 依赖链分析函数 ==========

def analyze_dependency_chain():
    """分析显示真实的依赖链结构"""
    
    print("\n🎯 真实多级依赖链结构：")
    print("1级: base_numbers → 2级: squared_numbers")
    print("1级: operation_codes → 2级: operation_configs") 
    print("2级: squared_numbers + operation_configs → 3级: processed_results")
    print("3级: processed_results → 4级: quality_assessment")
    print("4级: quality_assessment → 5级: final_report")
    
    print("\n📊 理论组合计算：")
    print(f"   base_numbers: {len(base_numbers())}个数字")
    print(f"   operation_codes: {len(operation_codes())}个操作")
    print(f"   threshold_levels: {len(threshold_levels())}个阈值")
    
    expected_cases = len(base_numbers()) * len(operation_codes()) * len(threshold_levels())
    actual_cases = len(final_report())
    
    print("\n🧮 组合结果：")
    print(f"   理论组合数: {expected_cases}")
    print(f"   实际生成数: {actual_cases}")
    
    assert expected_cases == actual_cases, f"组合数不匹配: {expected_cases} vs {actual_cases}"
    print("✅ 依赖链组合验证正确！")

def test_dependency_chain():
    """测试依赖链的正确性"""
    
    # 获取所有结果进行分析
    reports = final_report()
    
    # 验证每个结果都包含完整的依赖链信息
    for report in reports:
        assert "full_chain" in report
        assert "original_number" in report
        assert "final_result" in report
        assert "quality" in report
        assert report["level"] == 5
    
    print(f"✅ 5级依赖链测试通过，共生成 {len(reports)} 个测试用例")

# ========== 测试用例展示真实的依赖链 ==========

@pytest.mark.parametrize("result", processed_results)
def test_level_3_chain(result):
    """测试第3级依赖链"""
    assert result["level"] == 3
    assert result["squared"] == result["original"] ** 2

@pytest.mark.parametrize("result", quality_assessment)
def test_level_4_chain(result):
    """测试第4级依赖链"""
    assert result["level"] == 4
    assert "assessment" in result

@pytest.mark.parametrize("report", final_report)
def test_level_5_chain(report):
    """测试第5级依赖链 - 完整的A→B→C→D→E"""
    assert report["level"] == 5
    assert "→" in report["full_chain"]  # 确保有链条符号
    print(f"   依赖链: {report['full_chain']}")

# ========== 演示执行 ==========

if __name__ == "__main__":
    print("🚀 真实多级链式依赖演示\n")
    
    analyze_dependency_chain()
    test_dependency_chain()
    
    print("\n✨ 多级链式核心价值：")
    print("1. 清晰的依赖路径：A → B → C 的结构化关系")
    print("2. 可组合性：多个独立路径可以汇聚")
    print("3. 可测试性：每个级别都可以单独测试")
    print("4. 可维护性：依赖关系明确，易于理解")
    
    # 展示一个完整的依赖链示例
    print("\n🔍 完整依赖链示例：")
    sample_report = final_report()[0]
    print(f"   {sample_report['full_chain']}")
    
    print("\n✅ 真实多级链式功能验证完成！")