"""错误处理模块"""

from typing import List


class DynamicParamError(Exception):
    """动态参数系统基础异常"""
    pass


class MissingParameterError(DynamicParamError):
    """缺失参数异常"""
    
    def __init__(self, param_name: str, generator_name: str, 
                 required_params: List[str], available_params: List[str]):
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