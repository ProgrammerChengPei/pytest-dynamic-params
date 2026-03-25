"""插件工具函数模块"""

from typing import Any, Dict, List


class PluginUtils:
    """插件工具类"""

    @staticmethod
    def extract_dynamic_params(func) -> Dict[str, Any]:
        """提取函数中的动态参数映射

        Args:
            func: 函数对象

        Returns:
            动态参数映射字典
        """
        return getattr(func, "_mapping", {})

    @staticmethod
    def is_dynamic_parametrized(func) -> bool:
        """检查函数是否使用了 @dynamic_parametrize 装饰器

        Args:
            func: 函数对象

        Returns:
            是否使用了 @dynamic_parametrize 装饰器
        """
        return hasattr(func, "_is_parametrized")

    @staticmethod
    def is_use_generators(func) -> bool:
        """检查函数是否使用了 @use_generators 装饰器

        Args:
            func: 函数对象

        Returns:
            是否使用了 @use_generators 装饰器
        """
        return hasattr(func, "_is_mapped")

    @staticmethod
    def get_parametrize_info(func) -> List[Dict[str, Any]]:
        """获取函数的参数化信息

        Args:
            func: 函数对象

        Returns:
            参数化信息列表
        """
        return getattr(func, "_parametrize_info", [])

    @staticmethod
    def get_generator_mapping(func) -> Dict[str, Any]:
        """获取函数的生成器映射

        Args:
            func: 函数对象

        Returns:
            生成器映射字典
        """
        return getattr(func, "_mapping", {})
