"""
隐式依赖链式生成器示例 - 极简语法

🎯 核心优势：
1. 自动参数匹配：根据函数参数名自动查找对应的生成器
2. 零配置依赖：无需显式@pytest.mark.parametrize装饰器
3. 向后兼容：支持显式和隐式两种模式
"""

import pytest
from src.dynamic_params.public.decorators.implicit_generator import implicit_param_generator

# ========== 基础生成器定义（不变） ==========

@implicit_param_generator(scope="session") 
def data_source():
    """基础数据源生成器"""
    print("🔗 Fetching data from external source...")
    return [1, 2, 3, 4, 5]

@implicit_param_generator
def algorithm_list():
    """算法列表生成器"""
    return ["linear", "quadratic", "exponential"]

# ========== 隐式依赖的链式生成器 ==========

@implicit_param_generator  
def processor(algorithm):  # 💡 自动匹配 algorithm_list 生成器
    """处理器生成器 - 零配置参数依赖"""
    print(f"🔗 Initializing processor for {algorithm}")
    processors = {
        "linear": lambda x: x * 2,
        "quadratic": lambda x: x ** 2,
        "exponential": lambda x: 2 ** x
    }
    return processors[algorithm]

@implicit_param_generator
def process_data(data_source, processor):  # 💡 自动匹配 data_source 和 processor 生成器
    """链式数据处理 - 极简语法"""
    print(f"🔗 Processing data={data_source} with processor")
    return {
        "input": data_source,
        "output": processor(data_source),
        "processor_type": getattr(processor, '__name__', str(processor))
    }

# ========== 多级隐式依赖 ==========

@implicit_param_generator
def multiplier_list():
    """乘数生成器"""
    return [10, 20, 50]

@implicit_param_generator
def scaled_data(data_source, multiplier_list):  # 💡 自动双重依赖
    """缩放数据 - 多参数隐式依赖"""
    return [data_source * m for m in multiplier_list]

@implicit_param_generator
def final_result(scaled_data, processor):  # 💡 跨级隐式依赖
    """最终结果 - 链式处理"""
    return [processor(sd) for sd in scaled_data]

# ========== 混合模式（显式+隐式） ==========

@implicit_param_generator(explicit_mode=True)  # 📍 显式模式
@pytest.mark.parametrize("data", [100, 200])  # 显式参数
@implicit_param_generator  # 隐式模式
def mixed_mode_result(data, processor):  # 💡 processor自动匹配
    """混合模式示例：显式参数+隐式依赖"""
    return processor(data)

# ========== 智能错误处理示例 ==========

try:
    @implicit_param_generator
    def bad_example(non_existent_generator):  # 🚨 会报错：找不到匹配生成器
        """找不到依赖生成器的示例"""
        return non_existent_generator
        
except Exception as e:
    print(f"✅ 智能错误处理: {e}")

# ========== 测试用例 ==========

def test_implicit_dependencies():
    """测试隐式依赖功能"""
    
    # 基本生成器仍然正常工作
    assert algorithm_list() == ["linear", "quadratic", "exponential"]
    
    # 链式生成器自动获得参数
    processors = processor()
    assert len(processors) == 3  # 每个算法对应一个处理器
    
    print("✅ 隐式依赖功能测试通过")

# ========== 原生pytest兼容性测试 ==========

@pytest.mark.parametrize("result", process_data)  # 完全兼容原生pytest
def test_native_compatibility(result):
    """测试与原生pytest.mark.parametrize的兼容性"""
    assert isinstance(result, dict)
    assert "input" in result
    assert "output" in result
    print(f"✅ 原生兼容性测试: {result}")

# ========== 演示和验证 ==========

if __name__ == "__main__":
    print("🎯 隐式依赖链式生成器演示\n")
    
    # 展示隐式依赖的实际效果
    print("🔗 processor生成的参数数量:", len(process_data()))
    print("🔗 scaled_data的缩放结果:", scaled_data()[:2])  # 显示前2个
    print("🔗 final_result的计算结果:", final_result()[:2])  # 显示前2个
    
    print("\n✨ 隐式依赖的优势：")
    print("1. 零配置：无需额外的@pytest.mark.parametrize")
    print("2. 智能匹配：根据参数名自动查找生成器")
    print("3. 完全兼容：支持混合模式和原生pytest")
    
    # 运行测试
    test_implicit_dependencies()
    print("\n✅ 隐式依赖演示完成！")