"""性能测试工具模块"""

import psutil
import os


def get_current_memory_usage() -> int:
    """获取当前进程的内存使用情况（单位：MB）"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss // 1024 // 1024


def measure_memory_usage(func, *args, **kwargs) -> tuple:
    """测量函数执行的内存使用情况
    
    返回：(执行结果, 内存使用增量MB)
    """
    # 执行前内存使用
    before = get_current_memory_usage()
    
    # 执行函数
    result = func(*args, **kwargs)
    
    # 执行后内存使用
    after = get_current_memory_usage()
    
    # 计算内存使用增量
    memory_increase = after - before
    
    return result, memory_increase
