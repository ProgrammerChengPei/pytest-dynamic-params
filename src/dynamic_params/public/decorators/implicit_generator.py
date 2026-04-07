"""
隐式依赖链式生成器装饰器 - 严格匹配版本
支持跨文件查找，要求参数名和依赖生成器名完全一致
"""

import inspect
import os
from typing import Callable, List, Optional

import pytest

from ...engine.generator.registry import registry as generator_registry
from .param_generator import param_generator


def _find_test_files() -> List[str]:
    """查找pytest默认能识别的测试文件
    
    搜索规则：
    1. 当前目录及子目录下的所有.py文件
    2. 符合pytest测试文件命名约定的文件（test_*.py, *_test.py）
    3. 排除venv、__pycache__等目录
    """
    test_files = []
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "../../../.."))
    
    for root, dirs, files in os.walk(project_root):
        # 排除虚拟环境、缓存等目录
        dirs[:] = [d for d in dirs if not d.startswith(('.', '_')) and 'venv' not in d and 'cache' not in d]
        
        for file in files:
            if (file.startswith('test_') or file.endswith('_test.py')) and file.endswith('.py'):
                test_files.append(os.path.join(root, file))
    
    return test_files

def _find_matching_generator(param_name: str) -> Optional[str]:
    """严格匹配：参数名必须和生成器名完全一致
    
    匹配规则：
    1. 精确匹配参数名（必须完全一致）
    2. 支持跨文件查找
    """
    # 首先在本地注册表中查找
    if param_name in generator_registry:
        return param_name
    
    # 如果本地找不到，尝试动态导入其他文件中的生成器
    test_files = _find_test_files()
    
    for test_file in test_files:
        try:
            # 动态导入模块
            module_name = os.path.splitext(os.path.basename(test_file))[0]
            spec = importlib.util.spec_from_file_location(module_name, test_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 查找模块中的生成器函数
                for attr_name in dir(module):
                    if attr_name == param_name:
                        attr = getattr(module, attr_name)
                        # 检查是否被@param_generator装饰过
                        if hasattr(attr, '__wrapped__') or _is_param_generator(attr):
                            return attr_name
                            
        except Exception:
            continue
    
    return None

def _is_param_generator(func: Callable) -> bool:
    """检查函数是否被@param_generator装饰过"""
    return hasattr(func, '__wrapped__') and hasattr(func.__wrapped__, '_param_generator_registered')

def _inject_implicit_parametrize(func: Callable) -> Callable:
    """隐式注入@pytest.mark.parametrize装饰器"""
    sig = inspect.signature(func)
    
    # 收集需要隐式注入的参数
    implicit_parametrize_args = []
    
    for param_name, param in sig.parameters.items():
        # 跳过固定参数
        if param_name in ['self', 'cls']:
            continue
            
        # 查找匹配的生成器
        matching_gen = _find_matching_generator(param_name)
        if matching_gen:
            implicit_parametrize_args.append((param_name, matching_gen))
    
    # 如果有隐式依赖，构造新的装饰函数
    if implicit_parametrize_args:
        # 保存原始函数
        original_func = func
        
        # 构建隐式parametrize装饰器链
        decorated_func = original_func
        for param_name, gen_name in reversed(implicit_parametrize_args):
            gen_func = generator_registry[gen_name].func
            decorated_func = pytest.mark.parametrize(param_name, gen_func)(decorated_func)
        
        # 应用原始的@param_generator装饰器
        decorated_func = param_generator(decorated_func)
        
        return decorated_func
    
    return func

def implicit_param_generator(func: Optional[Callable] = None, *, 
                           scope: Optional[str] = None,
                           cache: bool = False, 
                           lazy: bool = False,
                           explicit_mode: bool = False) -> Callable:
    """隐式依赖参数生成器装饰器
    
    核心特性：
    1. 自动根据参数名查找匹配的生成器
    2. 可选显式模式（保持向后兼容）
    3. 智能异常处理：找不到生成器时提供清晰提示
    
    Args:
        explicit_mode: True=强制显式模式，False=自动隐式模式
    
    Examples:
        # 隐式模式（无需@pytest.mark.parametrize）
        @implicit_param_generator  
        def process_data(data_source, processor):  # 自动匹配data_source和processor生成器
            return processor(data_source)
            
        # 显式模式（保持兼容性）
        @implicit_param_generator(explicit_mode=True)
        @pytest.mark.parametrize("data", data_source)  
        @pytest.mark.parametrize("proc", processor)  
        def process_data_explicit(data, proc):
            return proc(data)
    """
    
    def decorator(func: Callable) -> Callable:
        if explicit_mode:
            # 显式模式：直接使用原始param_generator
            return param_generator(scope=scope, cache=cache, lazy=lazy)(func)
        else:
            # 隐式模式：自动注入parametrize装饰器
            return _inject_implicit_parametrize(func)
    
    if func is None:
        return decorator
    return decorator(func)

# 快捷别名
chainable = implicit_param_generator