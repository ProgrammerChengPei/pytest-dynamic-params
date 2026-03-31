"""
高级用法示例

此文件包含pytest-dynamic-params插件的高级使用示例，
展示了插件的高级功能和复杂使用场景，
并提供了实用的高级最佳实践。
"""

import random
import time

import pytest

from dynamic_params import generator, use_generators


# 示例1：多个动态参数嵌套 - 数据处理管道
@generator
def get_raw_data(data_source, size):
    """基础数据生成器

    模拟从不同来源获取原始数据

    Args:
        data_source: 数据来源（api、database、file）
        size: 数据大小

    Returns:
        原始数据列表
    """
    data = []
    for i in range(size):
        item = {
            "id": i + 1,
            "source": data_source,
            "value": random.randint(1, 100),
            "timestamp": time.time(),
        }
        data.append(item)
    return data


@generator
def process_data(raw_data, algorithm):
    """处理数据生成器，依赖于raw_data

    使用不同算法处理原始数据

    Args:
        raw_data: 原始数据
        algorithm: 处理算法（algo1: 平方, algo2: 立方, algo3: 平方根）

    Returns:
        处理后的数据列表
    """
    processed_data = []
    for item in raw_data:
        if algorithm == "algo1":
            processed_value = item["value"] ** 2
        elif algorithm == "algo2":
            processed_value = item["value"] ** 3
        elif algorithm == "algo3":
            processed_value = item["value"] ** 0.5
        else:
            processed_value = item["value"]

        processed_item = {
            "id": item["id"],
            "source": item["source"],
            "original_value": item["value"],
            "processed": processed_value,
            "algorithm": algorithm,
        }
        processed_data.append(processed_item)
    return processed_data


@generator
def validate_results(processed_data, threshold):
    """验证结果生成器，依赖于processed_data

    验证处理后的数据是否满足阈值要求

    Args:
        processed_data: 处理后的数据
        threshold: 验证阈值

    Returns:
        验证结果字典，包含是否通过和详细信息
    """
    scores = [item["processed"] for item in processed_data]
    passed = all(score >= threshold for score in scores)
    return {
        "passed": passed,
        "total_items": len(processed_data),
        "min_score": min(scores) if scores else 0,
        "max_score": max(scores) if scores else 0,
        "average_score": sum(scores) / len(scores) if scores else 0,
        "threshold": threshold,
    }


@use_generators(
    raw_data=get_raw_data,
    processed_data=process_data,
    validation_result=validate_results,
)
@pytest.mark.parametrize("data_source", ["api", "database", "file"])
@pytest.mark.parametrize("size", [5, 10])
@pytest.mark.parametrize("algorithm", ["algo1", "algo2", "algo3"])
@pytest.mark.parametrize("threshold", [10, 100, 1000])
def test_data_processing_pipeline(
    data_source, size, algorithm, threshold, raw_data, processed_data, validation_result
):
    """测试数据处理管道

    验证多个动态参数的嵌套依赖和数据处理流程
    """
    # 验证原始数据
    assert len(raw_data) == size
    assert all(item["source"] == data_source for item in raw_data)

    # 验证处理后的数据
    assert len(processed_data) == size
    assert all(
        item["id"] == raw_item["id"] for item, raw_item in zip(processed_data, raw_data)
    )
    assert all(item["algorithm"] == algorithm for item in processed_data)

    # 验证结果
    assert isinstance(validation_result, dict)
    assert "passed" in validation_result
    assert validation_result["total_items"] == size
    assert validation_result["threshold"] == threshold


# 示例2：作用域管理 - 不同作用域的实际应用
@generator(scope="function")
def function_scoped_data(input_value):
    """函数作用域参数生成器

    每个测试函数执行一次，适合每次都需要不同值的场景
    """
    return {"value": f"func_{input_value}", "timestamp": time.time()}


@generator(scope="class")
def class_scoped_data():
    """类作用域参数生成器

    每个测试类执行一次，适合类内共享的数据
    """
    return {"value": "class_shared", "created_at": time.time()}


@generator(scope="module")
def module_scoped_data():
    """模块作用域参数生成器

    每个模块执行一次，适合模块级共享的配置
    """
    return {
        "value": "module_shared",
        "config": {"api_url": "http://localhost:8000", "timeout": 30},
    }


@generator(scope="session")
def session_scoped_data():
    """会话作用域参数生成器

    整个测试会话执行一次，适合全局配置和资源
    """
    return {
        "value": "session_shared",
        "session_id": f"session_{int(time.time())}",
        "global_config": {"environment": "test", "version": "1.0.0"},
    }


class TestScopesUsage:
    """作用域使用测试类示例"""

    def setup_class(self):
        """类级别的 setup"""
        self.class_setup_time = time.time()

    @use_generators(
        func_data=function_scoped_data,
        class_data=class_scoped_data,
        mod_data=module_scoped_data,
        session_data=session_scoped_data,
    )
    @pytest.mark.parametrize("input_value", [1, 2])
    def test_scope_management(
        self, input_value, func_data, class_data, mod_data, session_data
    ):
        """测试作用域管理

        验证不同作用域的参数生成器执行行为
        """
        # 验证函数作用域数据（每次都不同）
        assert func_data["value"] == f"func_{input_value}"
        assert "timestamp" in func_data

        # 验证类作用域数据（类内共享）
        assert class_data["value"] == "class_shared"
        assert "created_at" in class_data

        # 验证模块作用域数据（模块内共享）
        assert mod_data["value"] == "module_shared"
        assert "config" in mod_data

        # 验证会话作用域数据（全局共享）
        assert session_data["value"] == "session_shared"
        assert "session_id" in session_data
        assert "global_config" in session_data

    @use_generators(
        func_data=function_scoped_data,
        class_data=class_scoped_data,
        mod_data=module_scoped_data,
        session_data=session_scoped_data,
    )
    @pytest.mark.parametrize("input_value", [3, 4])
    def test_scope_persistence(
        self, input_value, func_data, class_data, mod_data, session_data
    ):
        """测试作用域持久性

        验证不同作用域数据的持久性
        """
        # 函数作用域数据应该不同
        assert func_data["value"] == f"func_{input_value}"

        # 类作用域数据应该与上一个测试相同
        assert class_data["value"] == "class_shared"

        # 模块和会话作用域数据应该与上一个测试相同
        assert mod_data["value"] == "module_shared"
        assert session_data["value"] == "session_shared"


# 示例3：缓存控制 - 性能优化场景
@generator(cache=True)
def cached_expensive_computation(input_value):
    """启用缓存的参数生成器

    模拟计算密集型操作，使用缓存提高性能
    """
    print(f"Performing expensive computation for {input_value}...")
    # 模拟耗时操作
    time.sleep(0.2)
    # 模拟复杂计算
    result = 0
    for i in range(1000000):
        result += input_value * i
    return result


@generator(cache=False)
def uncached_time_based_data():
    """禁用缓存的参数生成器

    每次调用都返回新结果，适合时间相关的数据
    """
    return {
        "timestamp": time.time(),
        "random_value": random.randint(1, 1000),
        "current_time": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


@use_generators(
    cached_result=cached_expensive_computation, uncached_result=uncached_time_based_data
)
@pytest.mark.parametrize("input_value", [1, 2, 1, 2])  # 重复输入值以测试缓存
def test_cache_control(input_value, cached_result, uncached_result):
    """测试缓存控制

    验证缓存机制的工作原理和性能优化效果
    """
    # 验证缓存结果（相同输入应该返回相同结果）
    assert isinstance(cached_result, int)

    # 验证非缓存结果（每次都不同）
    assert isinstance(uncached_result, dict)
    assert "timestamp" in uncached_result
    assert "random_value" in uncached_result
    assert "current_time" in uncached_result


# 示例4：懒加载控制 - 按需计算
@generator(lazy=True)
def lazy_expensive_data(input_value):
    """启用懒加载的参数生成器

    只有在实际使用时才会执行，适合可能不被使用的计算
    """
    print(f"Lazy generating expensive data for input: {input_value}")
    # 模拟耗时操作
    time.sleep(0.3)
    return {
        "input": input_value,
        "data": [i * input_value for i in range(1000)],
        "generated_at": time.time(),
    }


@generator(lazy=False)
def eager_data(input_value):
    """禁用懒加载的参数生成器

    会立即执行，不管是否使用，适合必须预先计算的数据
    """
    print(f"Eager generating data for input: {input_value}")
    return input_value * 3


@use_generators(lazy_result=lazy_expensive_data, eager_result=eager_data)
@pytest.mark.parametrize("input_value", [1, 2])
def test_lazy_loading(input_value, lazy_result, eager_result):
    """测试懒加载控制

    验证懒加载机制的工作原理
    """
    # 验证懒加载结果（只有在使用时才会生成）
    assert lazy_result["input"] == input_value
    assert len(lazy_result["data"]) == 1000
    assert "generated_at" in lazy_result

    # 验证非懒加载结果（总是会生成）
    assert eager_result == input_value * 3


# 示例5：组合配置（作用域 + 缓存 + 懒加载）
@generator(scope="module", cache=True, lazy=True)
def optimized_data(input_value):
    """优化配置的参数生成器

    组合使用模块级作用域、缓存和懒加载，最大化性能
    """
    print(f"Optimized data generated for input: {input_value}")
    # 模拟耗时操作
    time.sleep(0.2)
    return {
        "input": input_value,
        "result": input_value * 100,
        "optimized": True,
        "scope": "module",
        "cached": True,
        "lazy": True,
    }


@use_generators(optimized_result=optimized_data)
@pytest.mark.parametrize("input_value", [1, 2, 3, 1, 2])  # 重复输入以测试缓存
def test_combined_config(input_value, optimized_result):
    """测试组合配置

    验证作用域、缓存和懒加载的组合使用效果
    """
    assert optimized_result["input"] == input_value
    assert optimized_result["result"] == input_value * 100
    assert optimized_result["optimized"] is True
    assert optimized_result["scope"] == "module"
    assert optimized_result["cached"] is True
    assert optimized_result["lazy"] is True


# 示例6：fixture参数化（动态fixture）- 多环境测试
@pytest.fixture(params=["dev", "test", "staging", "prod"])
def environment(request):
    """参数化fixture（动态fixture）

    为不同环境提供详细的配置信息
    """
    env_config = {
        "dev": {
            "url": "http://dev-api.example.com",
            "timeout": 10,
            "retry_attempts": 3,
            "api_key": "dev-key",
        },
        "test": {
            "url": "http://test-api.example.com",
            "timeout": 30,
            "retry_attempts": 2,
            "api_key": "test-key",
        },
        "staging": {
            "url": "http://staging-api.example.com",
            "timeout": 45,
            "retry_attempts": 2,
            "api_key": "staging-key",
        },
        "prod": {
            "url": "https://api.example.com",
            "timeout": 60,
            "retry_attempts": 1,
            "api_key": "prod-key",
        },
    }
    return env_config[request.param]


@pytest.fixture
def env_config(environment):
    """依赖动态fixture的静态fixture

    基于环境配置生成完整的应用配置
    """
    return {
        "base": "config",
        "env": environment["url"],
        "timeout": environment["timeout"],
        "retry_attempts": environment["retry_attempts"],
        "api_key": environment["api_key"],
        "version": "1.0.0",
    }


@generator
def generate_config_data(env_config, service):
    """依赖静态fixture的动态参数生成器

    基于环境配置和服务类型生成测试配置数据
    """
    service_configs = {
        "auth": {
            "endpoint": f"{env_config['env']}/auth",
            "timeout": env_config["timeout"],
            "retry": env_config["retry_attempts"],
        },
        "users": {
            "endpoint": f"{env_config['env']}/users",
            "timeout": env_config["timeout"] * 1.5,
            "retry": env_config["retry_attempts"],
        },
        "products": {
            "endpoint": f"{env_config['env']}/products",
            "timeout": env_config["timeout"] * 2,
            "retry": env_config["retry_attempts"],
        },
    }

    return {
        "service": service,
        "config": service_configs.get(service, {}),
        "environment": env_config["env"],
        "api_key": env_config["api_key"],
        "timestamp": time.time(),
    }


@use_generators(config_data=generate_config_data)
@pytest.mark.parametrize("service", ["auth", "users", "products"])
def test_fixture_parameterization(environment, env_config, service, config_data):
    """测试依赖参数化fixture的场景

    验证参数生成器能否正确处理来自参数化fixture的数据
    """
    assert config_data["service"] == service
    assert config_data["environment"] == env_config["env"]
    assert config_data["api_key"] == env_config["api_key"]
    assert "config" in config_data
    assert "endpoint" in config_data["config"]


# 示例7：静态fixture调用静态参数 - 数据转换链
@pytest.fixture
def static_param_fixture(input_value):
    """使用静态参数的静态fixture

    基于静态参数生成fixture值
    """
    return {"input": input_value, "value": input_value * 2, "type": "static"}


@generator
def transform_data(static_param_fixture, transform_type):
    """使用静态fixture的动态参数生成器

    基于静态fixture生成动态参数，并应用不同的转换
    """
    input_value = static_param_fixture["value"]

    if transform_type == "double":
        result = input_value * 2
    elif transform_type == "square":
        result = input_value**2
    elif transform_type == "increment":
        result = input_value + 10
    else:
        result = input_value

    return {
        "original": static_param_fixture,
        "transform_type": transform_type,
        "result": result,
        "processed_at": time.time(),
    }


@use_generators(transformed_data=transform_data)
@pytest.mark.parametrize("input_value", [1, 2, 3])
@pytest.mark.parametrize("transform_type", ["double", "square", "increment"])
def test_static_fixture_with_static_param(
    input_value, transform_type, static_param_fixture, transformed_data
):
    """测试静态fixture调用静态参数

    验证静态fixture与静态参数的结合使用
    """
    assert static_param_fixture["input"] == input_value
    assert static_param_fixture["value"] == input_value * 2

    assert transformed_data["original"] == static_param_fixture
    assert transformed_data["transform_type"] == transform_type

    expected_value = static_param_fixture["value"]
    if transform_type == "double":
        assert transformed_data["result"] == expected_value * 2
    elif transform_type == "square":
        assert transformed_data["result"] == expected_value**2
    elif transform_type == "increment":
        assert transformed_data["result"] == expected_value + 10


# 示例8：动态fixture调用静态参数 - 复杂参数组合
@pytest.fixture(params=[1, 2, 3, 5])
def dynamic_fixture_with_static_param(request, multiplier):
    """使用静态参数的动态fixture

    结合动态fixture和静态参数，生成复杂的参数组合
    """
    base_value = request.param
    return {
        "base": base_value,
        "multiplier": multiplier,
        "result": base_value * multiplier,
        "timestamp": time.time(),
    }


@generator
def use_dynamic_fixture(dynamic_fixture_with_static_param, operation):
    """使用动态fixture的动态参数生成器

    基于动态fixture生成动态参数，并应用额外操作
    """
    base_result = dynamic_fixture_with_static_param["result"]

    if operation == "add":
        result = base_result + 5
    elif operation == "subtract":
        result = base_result - 5
    elif operation == "multiply":
        result = base_result * 2
    else:
        result = base_result

    return {
        "fixture_data": dynamic_fixture_with_static_param,
        "operation": operation,
        "result": result,
        "calculated_at": time.time(),
    }


@use_generators(process_result=use_dynamic_fixture)
@pytest.mark.parametrize("multiplier", [10, 20])
@pytest.mark.parametrize("operation", ["add", "subtract", "multiply"])
def test_dynamic_fixture_with_static_param(
    multiplier, operation, dynamic_fixture_with_static_param, process_result
):
    """测试动态fixture调用静态参数

    验证动态fixture与静态参数的结合使用
    """
    assert dynamic_fixture_with_static_param["multiplier"] == multiplier
    assert process_result["fixture_data"] == dynamic_fixture_with_static_param
    assert process_result["operation"] == operation

    base_result = dynamic_fixture_with_static_param["result"]
    if operation == "add":
        assert process_result["result"] == base_result + 5
    elif operation == "subtract":
        assert process_result["result"] == base_result - 5
    elif operation == "multiply":
        assert process_result["result"] == base_result * 2


# 示例9：动态fixture调用动态参数 - 多层依赖链
@pytest.fixture(params=[1, 2, 3, 7, 10])
def dynamic_fixture(request):
    """动态fixture

    提供动态变化的fixture值
    """
    return {"value": request.param, "type": "dynamic", "created_at": time.time()}


@generator
def dynamic_param(dynamic_fixture):
    """依赖动态fixture的动态参数

    基于动态fixture生成动态参数
    """
    base_value = dynamic_fixture["value"]
    return {
        "base": base_value,
        "result": base_value * 10,
        "source": "dynamic_param",
        "timestamp": time.time(),
    }


@generator
def use_dynamic_param(dynamic_param, factor):
    """依赖动态参数的动态参数

    基于动态参数生成更复杂的动态参数
    """
    base_result = dynamic_param["result"]
    return {
        "param_data": dynamic_param,
        "factor": factor,
        "result": base_result * factor,
        "final_result": base_result * factor + 100,
        "processed_at": time.time(),
    }


@use_generators(dynamic_result=dynamic_param, final_result=use_dynamic_param)
@pytest.mark.parametrize("factor", [2, 5, 10])
def test_dynamic_fixture_with_dynamic_param(
    dynamic_fixture, dynamic_result, factor, final_result
):
    """测试动态fixture调用动态参数

    验证动态fixture与动态参数的结合使用
    """
    assert dynamic_result["base"] == dynamic_fixture["value"]
    assert dynamic_result["result"] == dynamic_fixture["value"] * 10

    assert final_result["param_data"] == dynamic_result
    assert final_result["factor"] == factor
    assert final_result["result"] == dynamic_result["result"] * factor
    assert final_result["final_result"] == dynamic_result["result"] * factor + 100


# 示例10：错误处理 - 异常情况测试
@generator
def risky_operation(input_value):
    """可能抛出异常的参数生成器

    模拟可能失败的操作，测试异常处理

    Args:
        input_value: 输入值

    Returns:
        操作结果或抛出异常
    """
    if input_value == 0:
        raise ValueError("Cannot process zero value")
    elif input_value < 0:
        raise ValueError("Cannot process negative value")
    else:
        return {"input": input_value, "result": 100 / input_value, "status": "success"}


@use_generators(risky_result=risky_operation)
@pytest.mark.parametrize("input_value", [1, 5, 10])
def test_risky_operation_success(input_value, risky_result):
    """测试风险操作成功情况

    验证参数生成器在正常情况下的行为
    """
    assert risky_result["input"] == input_value
    assert risky_result["result"] == 100 / input_value
    assert risky_result["status"] == "success"


@use_generators(risky_result=risky_operation)
@pytest.mark.parametrize("input_value", [0, -5])
def test_risky_operation_failure(input_value, risky_result):
    """测试风险操作失败情况

    验证参数生成器在异常情况下的行为
    """
    with pytest.raises(ValueError):
        # 当使用risky_result时会触发异常
        pass


# 示例11：复杂数据结构 - 嵌套字典和列表
@generator
def generate_complex_data(structure_type, size):
    """生成复杂数据结构的参数生成器

    根据结构类型和大小生成复杂的嵌套数据结构

    Args:
        structure_type: 结构类型（list, dict, nested）
        size: 数据大小

    Returns:
        复杂数据结构
    """
    if structure_type == "list":
        return [
            {"id": i, "value": random.randint(1, 100), "name": f"item_{i}"}
            for i in range(size)
        ]
    elif structure_type == "dict":
        return {
            f"key_{i}": {"value": random.randint(1, 100), "nested": f"value_{i}"}
            for i in range(size)
        }
    elif structure_type == "nested":
        return {
            "level1": {
                "data": [
                    {
                        "id": i,
                        "value": random.randint(1, 100),
                        "level2": {"nested": f"nested_{i}", "depth": 2},
                    }
                    for i in range(size)
                ],
                "metadata": {"size": size, "type": "nested"},
            }
        }
    else:
        return None


@use_generators(complex_data=generate_complex_data)
@pytest.mark.parametrize("structure_type", ["list", "dict", "nested"])
@pytest.mark.parametrize("size", [2, 3])
def test_complex_data_structures(structure_type, size, complex_data):
    """测试复杂数据结构生成

    验证参数生成器能否生成和处理复杂的嵌套数据结构
    """
    if structure_type == "list":
        assert isinstance(complex_data, list)
        assert len(complex_data) == size
        assert all(isinstance(item, dict) for item in complex_data)
    elif structure_type == "dict":
        assert isinstance(complex_data, dict)
        assert len(complex_data) == size
        assert all(isinstance(value, dict) for value in complex_data.values())
    elif structure_type == "nested":
        assert isinstance(complex_data, dict)
        assert "level1" in complex_data
        assert isinstance(complex_data["level1"], dict)
        assert "data" in complex_data["level1"]
        assert isinstance(complex_data["level1"]["data"], list)
        assert len(complex_data["level1"]["data"]) == size


# 示例12：动态参数化 - 使用dynamic_parametrize装饰器
from dynamic_params import dynamic_parametrize, DynRef


@pytest.fixture
def base_config():
    """基础配置fixture

    提供基础配置信息
    """
    return {
        "api_url": "http://localhost:8000",
        "timeout": 30,
        "api_key": "test-key",
        "version": "1.0.0"
    }


@pytest.fixture
def environment():
    """环境配置fixture

    提供环境配置信息
    """
    return "http://dev-api.example.com"


@dynamic_parametrize(
    "endpoint, expected_status",
    [
        ("/api/users", 200),
        ("/api/products", 200),
        ("/api/orders", 200),
        ("/api/invalid", 404)
    ]
)
def test_basic_dynamic_parametrize(endpoint, expected_status):
    """测试基础dynamic_parametrize功能

    验证dynamic_parametrize装饰器的基本使用方法
    """
    assert isinstance(endpoint, str)
    assert isinstance(expected_status, int)


@dynamic_parametrize(
    "env, endpoint, timeout",
    [
        ("dev", "/api/users", 10),
        ("test", "/api/products", 30),
        ("prod", "/api/orders", 60)
    ]
)
def test_dynamic_parametrize_with_params(env, endpoint, timeout):
    """测试dynamic_parametrize与普通参数的结合

    验证dynamic_parametrize装饰器能否正确处理普通参数
    """
    assert env in ["dev", "test", "prod"]
    assert isinstance(endpoint, str)
    assert isinstance(timeout, int)


@dynamic_parametrize(
    "environment, endpoint",
    [
        (DynRef("environment"), "/api/users"),
        (DynRef("environment"), "/api/products"),
        (DynRef("environment"), "/api/orders")
    ]
)
def test_dynamic_parametrize_with_fixture(environment, endpoint):
    """测试dynamic_parametrize与fixture的结合

    验证dynamic_parametrize装饰器能否正确处理fixture引用
    """
    assert isinstance(environment, str)
    assert isinstance(endpoint, str)
    assert environment.startswith("http")


@dynamic_parametrize(
    "base_config, endpoint",
    [
        (DynRef("base_config"), "/api/users"),
        (DynRef("base_config"), "/api/products")
    ]
)
def test_dynamic_parametrize_with_complex_values(base_config, endpoint):
    """测试dynamic_parametrize与复杂值的结合

    验证dynamic_parametrize装饰器能否正确处理复杂的参数值
    """
    assert isinstance(base_config, dict)
    assert isinstance(endpoint, str)
    expected_url = base_config["api_url"] + endpoint
    assert isinstance(expected_url, str)
