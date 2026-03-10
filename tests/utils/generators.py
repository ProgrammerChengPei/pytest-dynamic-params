"""
测试生成器函数
"""
from dynamic_params import param_generator


# 测试异常生成器
@param_generator
def failing_generator():
    """执行失败的生成器"""
    raise ValueError("生成器执行失败")


# 测试依赖生成器
@param_generator
def dependency_generator(value):
    """依赖其他参数的生成器"""
    return value * 2


# 测试缓存生成器
@param_generator(scope="module", cache=True)
def cached_generator():
    """带缓存的生成器"""
    import time
    time.sleep(0.1)  # 模拟耗时操作
    return "cached_value"


# 测试懒加载生成器
@param_generator(lazy=True)
def lazy_generator(value):
    """懒加载生成器"""
    import time
    time.sleep(0.1)  # 模拟耗时操作
    return value * 2
