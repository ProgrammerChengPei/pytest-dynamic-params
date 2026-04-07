# 链式参数生成器装饰器

import inspect
from typing import Callable, Optional

from ...engine.generator.base import GeneratorBase
from ...engine.generator.lazy import LazyGenerator
from ...engine.generator.registry import registry as generator_registry


def _infer_scope_dependencies(func_definition: str) -> str:
    """推断依赖生成器的最小scope
    
    根据待办文件要求："取它们中的最小范围"
    例如：gen_result 依赖 data 和 processor，processor 依赖 algorithm，取最小范围
    
    实现逻辑：
    1. 解析@pytest.mark.parametrize中的生成器引用
    2. 查找每个依赖生成器的scope
    3. 返回最小（最严格）的scope级别
    
    参数:
        func_definition: 函数定义源代码
        
    返回:
        推断的最小scope级别
    """
    import re

    # Scope优先级映射（数字越小优先级越高，范围越小）
    SCOPE_PRIORITY = {"function": 1, "class": 2, "module": 3, "session": 4}
    scopes_found = []
    
    # 匹配@pytest.mark.parametrize装饰器中的生成器引用
    parametrize_pattern = r'@pytest\.mark\.parametrize\([^)]+\)'
    parametrize_matches = re.findall(parametrize_pattern, func_definition)
    
    for match in parametrize_matches:
        # 提取生成器名称（第二个参数）
        args_match = re.search(r'@pytest\.mark\.parametrize\(\s*"[^"]+"\s*,\s*(\w+)', match)
        if args_match:
            gen_name = args_match.group(1)
            if gen_name in generator_registry:
                gen_obj = generator_registry[gen_name]
                if hasattr(gen_obj, 'scope'):
                    scopes_found.append(gen_obj.scope)
    
    # 如果没有找到依赖生成器，使用默认function级
    if not scopes_found:
        return "function"
    
    # 取最小（最严格）的scope
    min_scope = min(scopes_found, key=lambda s: SCOPE_PRIORITY.get(s, 999))
    return min_scope

def param_generator(func: Optional[Callable] = None, *, 
                   scope: Optional[str] = None,
                   cache: bool = False, 
                   lazy: bool = False) -> Callable:
    """链式参数生成器装饰器 - 支持显式依赖声明
    
    关键特性：
    1. 使用@pytest.mark.parametrize显式声明参数依赖关系
    2. scope参数控制生成器的复用级别
    3. 完全兼容原生pytest.mark.parametrize装饰器
    
    Args:
        func: 生成器函数
        scope: 作用域级别 ("function", "class", "module", "session")
        cache: 是否缓存结果
        lazy: 是否延迟加载
        
    Returns:
        装饰后的生成器函数
        
    Examples:
        # 基础生成器
        @param_generator(scope="session")
        def data_source():
            return [1, 2, 3]
        
        # 显式依赖生成器
        @param_generator(scope="function")
        @pytest.mark.parametrize("algorithm", algorithms)  
        def processor(algorithm):
            return processors[algorithm]
        
        # 链式生成器
        @param_generator(scope="function")
        @pytest.mark.parametrize("data", data_source)  
        @pytest.mark.parametrize("processor", processor)  
        def gen_result(data, processor):
            return processor(data)
    """
    
    def decorator(func: Callable) -> Callable:
        # 获取函数的装饰器信息
        func_source = inspect.getsource(func)
        
        # 智能scope推断逻辑
        final_scope = scope
        if final_scope is None:
            # 解析函数定义行的上一行，查找@pytest.mark.parametrize装饰器
            # 这里简化实现，实际应该更精确解析代码结构
            final_scope = "function"  # 默认值
            
            # TODO: 实现更精确的装饰器解析逻辑
            # 检查是否有@pytest.mark.parametrize装饰器
            if '@pytest.mark.parametrize' in func_source:
                # 如果有参数依赖，使用自动推断scope
                final_scope = "function"  # 链式生成器通常是最小scope
        
        # 确定生成器类
        generator_class = LazyGenerator if lazy else GeneratorBase
        
        # 创建生成器实例
        generator = generator_class(
            func,
            scope=final_scope,
            cache=cache
        )
        
        # 注册生成器
        generator_registry.register(func.__name__, generator)
        
        # 返回原始函数（保持兼容性）
        return func
    
    # 处理装饰器使用情况
    if func is None:
        return decorator
    return decorator(func)
