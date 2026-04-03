"""
外部资源生成器使用示例

这个文件展示了如何在实际项目中使用支持外部资源的生成器。

场景包括：
1. 数据库访问
2. 网络 API 调用
3. 文件系统
4. 混合场景
"""

import pytest
from dynamic_params import parametrize_test, parametrize_generator, param_generator


# ============================================================================
# 场景 1：数据库访问 - 预加载静态数据
# ============================================================================

@param_generator(
    scope='session',
    cache=True
)
def generate_test_users():
    """
    从数据库加载测试用户
    
    只在主进程执行一次，所有 worker 共享数据
    """
    # 模拟数据库查询
    print("[generate_test_users] Loading users from database...")
    
    # 实际项目中：
    # import database
    # conn = database.connect()
    # cursor = conn.cursor()
    # cursor.execute("SELECT id, username, email FROM users WHERE active = true")
    # users = [
    #     {'id': row[0], 'username': row[1], 'email': row[2]}
    #     for row in cursor.fetchall()
    # ]
    
    # 示例数据
    users = [
        {'id': 1, 'username': 'alice', 'email': 'alice@example.com'},
        {'id': 2, 'username': 'bob', 'email': 'bob@example.com'},
        {'id': 3, 'username': 'charlie', 'email': 'charlie@example.com'},
    ]
    
    print(f"[generate_test_users] Loaded {len(users)} users")
    return users


# ============================================================================
# 场景 2：数据库访问 - Worker 独立连接（动态数据）
# ============================================================================

@param_generator(scope='function')
def generate_realtime_orders():
    """
    实时订单数据
    
    每个 worker 独立查询数据库，获取最新数据
    适用于：
    - 数据实时变化
    - 需要最新状态
    - 数据量太大无法预加载
    """
    # 每个 worker 都会执行这里
    worker_id = __import__('os').environ.get('PYTEST_XDIST_WORKER', 'master')
    pid = __import__('os').getpid()
    print(f"[generate_realtime_orders] Worker {worker_id} (PID: {pid})")
    
    # 使用连接池（模拟）
    orders = [
        {'id': 101, 'status': 'pending', 'amount': 99.99},
        {'id': 102, 'status': 'completed', 'amount': 149.99},
    ]
    
    for order in orders:
        yield order


# ============================================================================
# 场景 3：网络 API 调用 - 带缓存和回退
# ============================================================================

@param_generator(
    scope='session',
    cache=True
)
def generate_exchange_rates():
    """
    从外部 API 获取汇率
    
    只在主进程调用一次 API，避免：
    - API 限流
    - 网络延迟
    - 数据不一致
    """
    print("[generate_exchange_rates] Fetching exchange rates from API...")
    
    try:
        # 实际项目中：
        # import requests
        # response = requests.get(
        #     'https://api.exchangerate.com/latest',
        #     timeout=5
        # )
        # response.raise_for_status()
        # rates = response.json()['rates']
        
        # 示例数据
        rates = {
            'USD': 1.0,
            'EUR': 0.85,
            'GBP': 0.73,
            'JPY': 110.0,
        }
        
        print(f"[generate_exchange_rates] Loaded {len(rates)} rates")
        return rates
    
    except Exception as e:
        print(f"[generate_exchange_rates] API failed: {e}, using fallback")
        # 回退数据
        return {
            'USD': 1.0,
            'EUR': 0.85,
            'GBP': 0.73,
        }


# ============================================================================
# 场景 4：文件系统 - 加载配置文件
# ============================================================================

@param_generator(scope='session', cache=True)
def generate_config_files():
    """
    从文件系统加载配置文件
    
    主进程加载一次，所有 worker 共享
    """
    print("[generate_config_files] Loading configuration files...")
    
    from pathlib import Path
    
    configs = []
    config_dir = Path('tests/fixtures/configs')
    
    if config_dir.exists():
        for config_file in config_dir.glob('*.json'):
            with open(config_file, 'r') as f:
                import json
                config = json.load(f)
                configs.append({
                    'file': config_file.name,
                    'content': config
                })
    else:
        # 示例配置
        configs = [
            {'file': 'app.json', 'content': {'debug': False, 'timeout': 30}},
            {'file': 'db.json', 'content': {'host': 'localhost', 'port': 5432}},
        ]
    
    print(f"[generate_config_files] Loaded {len(configs)} configs")
    return configs


# ============================================================================
# 场景 5：混合场景 - 组合使用
# ============================================================================

def test_user_order_scenario():
    """
    测试用户订单场景
    
    - user: 预加载的静态用户数据
    - order: 实时订单数据（每个 worker 独立查询）
    """
    @parametrize_test("user", generate_test_users)
    @parametrize_test("order", generate_realtime_orders)
    def _test(user, order):
        assert 'username' in user
        assert 'id' in order
        print(f"Testing user {user['username']} with order {order['id']}")
    
    # 注意：这个测试展示了如何组合使用不同的生成器
    # 实际运行时，装饰器会自动展开所有参数组合


def test_currency_conversion():
    """
    测试货币转换
    
    使用预加载的汇率数据
    """
    @parametrize_test("rate", generate_exchange_rates)
    def _test(rate, value=100):
        assert isinstance(rate, (int, float))
        converted = value * rate
        print(f"{value} USD = {converted} (rate: {rate})")
    
    # 注意：这个测试展示了如何使用外部 API 数据
    # 汇率数据只在主进程加载一次，所有 worker 共享


# ============================================================================
# 场景 6：敏感数据处理
# ============================================================================

@param_generator(scope='session', cache=True)
def generate_secure_user_data():
    """
    敏感数据处理示例
    
    不序列化敏感字段（密码、token 等）
    """
    print("[generate_secure_user_data] Loading users (sanitized)...")
    
    # 示例数据（已脱敏）
    users = [
        {'id': 1, 'username': 'alice'},
        {'id': 2, 'username': 'bob'},
    ]
    
    print(f"[generate_secure_user_data] Loaded {len(users)} sanitized users")
    return users


# ============================================================================
# 场景 7：大数据集分批加载
# ============================================================================

@param_generator(scope='session', cache=True)
def generate_large_dataset():
    """
    大数据集分批加载
    
    避免一次性加载过多数据导致内存问题
    """
    print("[generate_large_dataset] Loading large dataset in batches...")
    
    # 模拟分批加载
    all_data = []
    batch_size = 1000
    total_batches = 5
    
    for batch_num in range(total_batches):
        # 模拟数据
        batch = [{'id': i} for i in range(batch_num * batch_size, (batch_num + 1) * batch_size)]
        all_data.extend(batch)
        
        print(f"[generate_large_dataset] Loaded batch {batch_num + 1}/{total_batches} ({len(all_data)} total)")
    
    print(f"[generate_large_dataset] Total: {len(all_data)} items")
    return all_data
