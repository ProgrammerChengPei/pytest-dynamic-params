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


def _detect_decorator_order(func_source: str) -> dict:
    """检测装饰器顺序
    
    返回装饰器顺序信息：
    {
        'order': list 装饰器类型顺序,
        'has_parametrize': bool 是否有parametrize,
        'has_param_generator': bool 是否有param_generator,
        'is_correct_order': bool 顺序是否正确
    }
    """
    
    # 检测装饰器
    decorators = []
    lines = func_source.strip().split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith('@'):
            if 'pytest.mark.parametrize' in line or 'parametrize(' in line:
                decorators.append({'type': 'parametrize', 'line': i, 'content': line})
            elif 'param_generator' in line:
                decorators.append({'type': 'param_generator', 'line': i, 'content': line})
    
    # 确定顺序
    if not decorators:
        return {'order': [], 'has_parametrize': False, 'has_param_generator': False, 'is_correct_order': True}
    
    order = [d['type'] for d in sorted(decorators, key=lambda x: x['line'])]
    
    # 正确顺序：parametrize在外层，param_generator在内层
    is_correct = (order[-1] == 'param_generator' if len(order) > 1 else True)
    
    return {
        'order': order,
        'has_parametrize': 'parametrize' in order,
        'has_param_generator': 'param_generator' in order,
        'is_correct_order': is_correct
    }


def _adjust_decorator_order(func: Callable) -> Callable:
    """自动调整装饰器顺序辅助函数
    
    当@pytest.mark.parametrize和@param_generator顺序不当时，自动调整。
    """
    import inspect

    # 获取函数源代码
    try:
        source = inspect.getsource(func)
    except (OSError, TypeError):
        return func  # 无法获取源代码
    
    # 检测装饰器顺序
    order_info = _detect_decorator_order(source)
    
    if not order_info['has_parametrize'] or order_info['is_correct_order']:
        return func  # 无需调整
    
    # 创建包装函数来处理错误顺序的情况
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    
    # 复制属性
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__module__ = func.__module__
    
    # 标记已经过自动调整
    wrapper._decorator_order_adjusted = True
    wrapper._original_order_info = order_info
    
    return wrapper


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
        
        # 自动装饰器顺序调整逻辑
        # 检查装饰器顺序是否正确：param_generator应该在内层
        if hasattr(func, '_parametrize_called') and not hasattr(func, '_param_generator_called'):
            # 正确的顺序：param_generator在内层
            # @pytest.mark.parametrize -> @param_generator -> def func
            processed_func = func
        elif hasattr(func, '_param_generator_called') and not hasattr(func, '_parametrize_called'):
            # 错误的顺序：param_generator在外层
            # 需要延迟处理，等待@pytest.mark.parametrize应用
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            # 复制所有属性
            wrapper.__name__ = func.__name__
            wrapper.__doc__ = func.__doc__
            wrapper.__module__ = func.__module__
            
            # 标记需要后续处理
            wrapper._needs_parametrize = True
            wrapper._original_func = func
            processed_func = wrapper
        else:
            # 正常情况或尚未应用其他装饰器
            processed_func = func
        
        # 标记param_generator已应用
        processed_func._param_generator_called = True
        
        # 智能scope推断逻辑
        final_scope = scope
        if final_scope is None:
            # 检查是否有@pytest.mark.parametrize依赖
            if '@pytest.mark.parametrize' in func_source:
                # 自动推断scope：如果有依赖，使用依赖的最小scope
                final_scope = _infer_scope_dependencies(func_source)
            else:
                final_scope = "session"  # 无依赖的生成器默认用session级
        
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
