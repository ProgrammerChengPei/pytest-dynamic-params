"""错误处理模块"""

from typing import Any, Dict, List


class DynamicParamError(Exception):
    """动态参数系统基础异常"""

    pass


class MissingParameterError(DynamicParamError):
    """缺失参数异常"""

    def __init__(
        self,
        param_name: str,
        generator_name: str,
        required_params: List[str],
        available_params: List[str],
    ):
        self.param_name = param_name
        self.generator_name = generator_name
        self.required_params = required_params
        self.available_params = available_params

        super().__init__(
            f"参数 '{param_name}' 在生成器函数 '{generator_name}' 中需要，但未在测试用例中找到。\n"
            f"生成器函数需要的参数: {required_params}\n"
            f"测试用例可用参数: {available_params}"
        )


class InvalidGeneratorError(DynamicParamError):
    """无效生成器异常"""

    def __init__(self, message: str):
        super().__init__(message)


class CircularDependencyError(DynamicParamError):
    """循环依赖异常"""

    def __init__(self, cycle: List[str]):
        self.cycle = cycle
        cycle_str = " -> ".join(cycle)
        super().__init__(
            f"检测到循环依赖:\n\n"
            f"依赖链: {cycle_str} -> {cycle[0]}\n\n"
            f"请修改生成器函数的依赖关系以消除循环。"
        )


class ExecutionError(DynamicParamError):
    """生成器执行异常"""

    def __init__(
        self, generator_name: str, exception: Exception, context: Dict[str, Any]
    ):
        self.generator_name = generator_name
        self.exception = exception
        self.context = context

        super().__init__(
            f"参数生成器 '{generator_name}' 执行失败:\n\n"
            f"异常类型: {type(exception).__name__}\n"
            f"异常信息: {str(exception)}\n"
            f"调用上下文: {context}\n"
        )


class ConfigurationError(DynamicParamError):
    """配置错误异常"""

    def __init__(self, config_key: str, config_value: Any, expected_type: type):
        self.config_key = config_key
        self.config_value = config_value
        self.expected_type = expected_type

        super().__init__(
            f"配置项 '{config_key}' 无效:\n\n"
            f"当前值: {config_value} (类型: {type(config_value).__name__})\n"
            f"期望类型: {expected_type.__name__}"
        )
