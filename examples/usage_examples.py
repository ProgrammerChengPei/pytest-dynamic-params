"""
动态参数化插件使用示例集合

该文件展示了 pytest-dynamic-params 插件的实际测试用例编写方法
每个示例都可以作为模板，复制到自己的测试文件中使用
"""

import pytest

from dynamic_params import param_generator, with_dynamic_params


# 示例1：基础用法
@param_generator
def calculate_result(input_value):
    """基础参数生成器"""
    return input_value * 2


@with_dynamic_params(result=calculate_result)
@pytest.mark.parametrize("input_value", [1, 2, 3])
def test_basic_usage(input_value, result):
    """基础用法测试示例"""
    assert result == input_value * 2


# 示例2：与fixture混合使用
@pytest.fixture
def database():
    """模拟数据库连接"""
    return {"users": {"admin": {"type": "admin"}, "user": {"type": "user"}}}


@param_generator
def get_user_data(database, user_type):
    """依赖于fixture的参数生成器"""
    return database["users"].get(user_type, {"type": "unknown"})


@with_dynamic_params(user_data=get_user_data)
@pytest.mark.parametrize("user_type", ["admin", "user"])
def test_with_fixture_integration(database, user_type, user_data):
    """与fixture混合使用测试示例"""
    assert user_data["type"] == user_type
    assert database["users"][user_type] is not None


# 示例3：参数化fixture支持
@pytest.fixture(params=["dev", "test", "prod"])
def environment(request):
    """参数化fixture"""
    return {"env": request.param, "timeout": 30}


@param_generator
def generate_config(environment, feature_flag):
    """依赖于参数化fixture的参数生成器"""
    return {
        "env": environment["env"],
        "feature": feature_flag,
        "timeout": environment["timeout"] + 10
    }


@with_dynamic_params(config=generate_config)
@pytest.mark.parametrize("feature_flag", ["A/B", "control"])
def test_parametrized_fixture_usage(environment, feature_flag, config):
    """参数化fixture测试示例"""
    assert config["env"] == environment["env"]
    assert config["feature"] == feature_flag
    assert config["timeout"] == environment["timeout"] + 10


# 示例4：多个fixture嵌套
@pytest.fixture
def base_config():
    """基础配置fixture"""
    return {"app": "test", "version": "1.0"}


@pytest.fixture
def database_config(base_config):
    """数据库配置fixture（依赖base_config）"""
    return {**base_config, "db": "postgresql"}


@pytest.fixture
def app_config(database_config):
    """应用配置fixture（依赖database_config）"""
    return {**database_config, "port": 8080}


@param_generator
def generate_test_data(app_config, test_type):
    """依赖于嵌套fixture的参数生成器"""
    return {
        "config": app_config,
        "type": test_type,
        "data": [1, 2, 3]
    }


@with_dynamic_params(test_data=generate_test_data)
@pytest.mark.parametrize("test_type", ["unit", "integration"])
def test_fixture_nesting_usage(app_config, test_type, test_data):
    """fixture嵌套依赖测试示例"""
    assert test_data["config"]["port"] == 8080
    assert test_data["type"] == test_type
    assert len(test_data["data"]) == 3


# 示例5：多个动态参数嵌套
@param_generator
def get_raw_data(data_source, size):
    """基础数据生成器"""
    return [{"id": i + 1, "source": data_source} for i in range(size)]


@param_generator
def process_data(raw_data, algorithm):
    """处理数据生成器，依赖于raw_data"""
    if algorithm == "algo1":
        return [{"id": item["id"], "processed": item["id"] * 2} for item in raw_data]
    else:
        return [{"id": item["id"], "processed": item["id"] * 3} for item in raw_data]


@param_generator
def validate_results(processed_data, threshold):
    """验证结果生成器，依赖于processed_data"""
    scores = [item["processed"] for item in processed_data]
    return all(score >= threshold for score in scores)


@with_dynamic_params(
    raw_data=get_raw_data,
    processed_data=process_data,
    is_valid=validate_results
)
@pytest.mark.parametrize("data_source", ["api", "database"])
@pytest.mark.parametrize("size", [5, 10])
@pytest.mark.parametrize("algorithm", ["algo1", "algo2"])
@pytest.mark.parametrize("threshold", [0.5, 8.0])
def test_dynamic_params_nesting_usage(
    data_source, size, algorithm, threshold,
    raw_data, processed_data, is_valid
):
    """多个动态参数嵌套依赖测试示例"""
    # 验证原始数据
    assert len(raw_data) == size
    assert all(item["source"] == data_source for item in raw_data)
    
    # 验证处理后的数据
    assert len(processed_data) == size
    assert all(item["id"] == raw_item["id"] for item, raw_item in zip(processed_data, raw_data))
    
    # 验证结果
    assert isinstance(is_valid, bool)


# 示例6：作用域管理
@param_generator(scope="function")
def function_scoped_data(input_value):
    """函数作用域参数生成器"""
    return f"func_{input_value}"


@param_generator(scope="class")
def class_scoped_data():
    """类作用域参数生成器"""
    return "class_shared"


@param_generator(scope="module")
def module_scoped_data():
    """模块作用域参数生成器"""
    return "module_shared"


class TestScopesUsage:
    """作用域使用测试类示例"""
    
    @with_dynamic_params(
        func_data=function_scoped_data,
        class_data=class_scoped_data,
        mod_data=module_scoped_data
    )
    @pytest.mark.parametrize("input_value", [1, 2])
    def test_scope_management(self, input_value, func_data, class_data, mod_data):
        """作用域管理测试示例"""
        assert func_data == f"func_{input_value}"
        assert class_data == "class_shared"
        assert mod_data == "module_shared"


# 使用指导：
# 1. 将此文件中的示例复制到你的测试文件中
# 2. 修改参数生成器函数以适应你的测试需求
# 3. 根据需要添加更多的参数化装饰器
# 4. 确保参数生成器函数的名称与with_dynamic_params中的键名匹配