from dynamic_params import param_generator


@param_generator
def generate_config(environment, feature_flag):
    """生成测试配置"""
    return {
        "env": environment["env"],
        "feature": feature_flag,
        "timeout": environment["timeout"] + 10
    }


@param_generator
def get_user_data(database, user_type):
    """从数据库获取用户数据"""
    return database["users"][user_type]


@param_generator
def generate_test_data(app_config, test_type):
    """生成测试数据"""
    return {
        "config": app_config,
        "type": test_type,
        "data": [1, 2, 3]
    }
