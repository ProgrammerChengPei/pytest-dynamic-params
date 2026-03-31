# Conftest file for pytest

import pytest

# Register the plugin
pytest_plugins = ('dynamic_params.plugin.pytest_plugin',)

def pytest_configure(config):
    """Configure pytest"""
    # Register custom markers
    config.addinivalue_line("markers", "dynamic_parametrize: mark a function for dynamic parametrization")


# ============================================================================
# 同步方案示例生成器
# ============================================================================

from dynamic_params import param_generator


@param_generator
def generate_simple():
    """普通生成器 - 行为不变"""
    yield from [1, 2, 3, 4, 5]


@param_generator(scope='session', cache=True)
def generate_session_users():
    """
    Session 级别生成器 - 自动预加载
    
    主进程执行一次，数据同步到所有 Worker
    不需要 preload=True 参数
    """
    print(f"[generate_session_users] Executing (PID: {__import__('os').getpid()})")
    
    # 模拟数据库查询
    users = [
        {'id': 1, 'username': 'alice'},
        {'id': 2, 'username': 'bob'},
        {'id': 3, 'username': 'charlie'},
    ]
    
    return users


@param_generator(scope='module', cache=True)
def generate_module_data():
    """
    Module 级别生成器 - 自动预加载
    
    每个 module 只执行一次
    """
    print(f"[generate_module_data] Executing (PID: {__import__('os').getpid()})")
    
    import random
    data = list(range(10))
    random.shuffle(data)
    return data[:5]


@param_generator(scope='function')
def generate_realtime_orders():
    """
    Function 级别生成器 - Worker 独立连接
    
    每个 Worker 有自己的数据库连接
    使用 WorkerPool 自动管理连接
    """
    worker_id = __import__('os').environ.get('PYTEST_XDIST_WORKER', 'master')
    pid = __import__('os').getpid()
    print(f"[generate_realtime_orders] Worker {worker_id} (PID: {pid})")
    
    # 使用连接池（模拟）
    orders = [
        {'id': 101, 'status': 'pending'},
        {'id': 102, 'status': 'completed'},
        {'id': 103, 'status': 'pending'},
    ]
    
    for order in orders:
        yield order


@param_generator(scope='session')
def generate_static_config():
    """静态配置 - 预加载"""
    print(f"[generate_static_config] Preloading (PID: {__import__('os').getpid()})")
    return {
        'timeout': 30,
        'retry': 3,
        'batch_size': 100
    }


@param_generator(scope='function')
def generate_dynamic_logs():
    """动态日志 - Worker 独立查询"""
    worker_id = __import__('os').environ.get('PYTEST_XDIST_WORKER', 'master')
    print(f"[generate_dynamic_logs] Worker {worker_id} querying logs")
    
    # 模拟查询
    logs = [
        {'id': 1, 'message': 'Log 1'},
        {'id': 2, 'message': 'Log 2'},
        {'id': 3, 'message': 'Log 3'},
    ]
    
    for log in logs:
        yield log

