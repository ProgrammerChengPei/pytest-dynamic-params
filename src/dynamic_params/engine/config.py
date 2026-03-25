import configparser
import os
from typing import Any, Dict, List, Optional

from ..errors import ConfigurationError


class DynamicParamConfig:
    """动态参数化系统配置类"""

    DEFAULT_CONFIG = {
        "cache": {
            "enabled": "true",
            "size_function": "1000",
            "size_class": "500",
            "size_module": "200",
            "size_session": "100",
            "cleanup_interval": "100",
            "dir": ".pytest_cache/dynamic_params",
        },
        "validation": {"level": "strict", "log_level": "INFO"},
        "performance": {
            "lazy_loading": "true",
            "incremental_generation": "true"
        },
        "debug": {"enabled": "false", "profile": "false"},
    }

    _instance: Optional["DynamicParamConfig"] = None
    _config: Dict[str, Any]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = cls._instance._load_config()
        return cls._instance

    @classmethod
    def get_instance(cls):
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """重置单例实例，用于测试"""
        cls._instance = None

    def load_from_dict(self, config_dict: Dict[str, Any]):
        """从字典加载配置，用于测试

        参数:
            config_dict: 配置字典
        """
        self._config = config_dict

    def _load_config(self, config_files: Optional[List[str]] = None) -> Dict[str, Any]:
        """加载配置

        参数:
            config_files: 配置文件路径列表，默认为 None，使用默认配置文件路径
        """
        config = configparser.ConfigParser()
        config.read_dict(self.DEFAULT_CONFIG)

        # 从配置文件加载（优先级：pytest.ini > pyproject.toml > dynamic_params.json/yaml）
        if config_files is None:
            config_files = [
                "pytest.ini",
                "pyproject.toml",
                "dynamic_params.json",
                "dynamic_params.yaml",
            ]

        for file in config_files:
            self._load_from_file(config, file)

        # 处理 pytest.dynamic_params 格式的配置节
        if "pytest.dynamic_params" in config:
            self._process_pytest_dynamic_params(config)

        return self._normalize_config(config)

    def _load_from_file(self, config: configparser.ConfigParser, file: str):
        """加载单个配置文件

        参数:
            config: 配置对象
            file: 配置文件路径
        """
        if os.path.exists(file):
            try:
                config.read(file)
            except Exception as e:
                print(f"Warning: Failed to read {file}: {e}")

    def _process_pytest_dynamic_params(self, config: configparser.ConfigParser):
        """处理 pytest.dynamic_params 格式的配置节

        参数:
            config: 配置对象
        """
        # 提取配置项并添加到相应的节
        for key, value in config["pytest.dynamic_params"].items():
            if key == "markers":
                # markers 特殊处理
                if "markers" not in config:
                    config["markers"] = {}
                config["markers"][key] = value
            elif key.startswith("cache_size_"):
                # 缓存大小配置
                cache_section = key.replace("cache_size_", "size_")
                if "cache" not in config:
                    config["cache"] = {}
                config["cache"][cache_section] = value
            elif key == "validation":
                # 验证级别
                if "validation" not in config:
                    config["validation"] = {}
                config["validation"]["level"] = value
            elif key == "log_level":
                # 日志级别
                if "validation" not in config:
                    config["validation"] = {}
                config["validation"]["log_level"] = value
            elif key == "lazy_loading":
                # 懒加载
                if "performance" not in config:
                    config["performance"] = {}
                config["performance"]["lazy_loading"] = value
            elif key == "incremental_generation":
                # 增量生成
                if "performance" not in config:
                    config["performance"] = {}
                config["performance"]["incremental_generation"] = value
            elif key == "cache_enabled":
                # 缓存启用
                if "cache" not in config:
                    config["cache"] = {}
                config["cache"]["enabled"] = value

    def _normalize_config(
        self,
        config: configparser.ConfigParser
    ) -> Dict[str, Any]:
        """标准化配置值"""
        normalized: Dict[str, Any] = {}

        for section in config.sections():
            normalized[section] = {}
            for key, value in config[section].items():
                try:
                    # 转换布尔值
                    if value.lower() in ("true", "false"):
                        normalized[section][key] = (
                            config[section].getboolean(key)
                        )
                    # 转换整数
                    elif value.isdigit():
                        normalized[section][key] = config[section].getint(key)
                    else:
                        normalized[section][key] = value
                except Exception as e:
                    raise ConfigurationError(
                        config_key=f"{section}.{key}",
                        config_value=value,
                        expected_type=str,
                    ) from e

        return normalized

    def get(
        self,
        section: str,
        option: str,
        default: Optional[Any] = ...
    ) -> Any:
        """获取配置值"""
        try:
            if section not in self._config:
                if default is not ...:
                    return default
                raise KeyError(section)
            if option not in self._config[section]:
                if default is not ...:
                    return default
                raise KeyError(option)
            return self._config[section][option]
        except KeyError:
            if default is not ...:
                return default
            raise

    def get_section(self, section: str) -> Dict[str, Any]:
        """获取整个配置节"""
        return self._config.get(section, {})

    def validate(self) -> bool:
        """验证配置有效性"""
        try:
            # 验证缓存配置
            if not isinstance(self.get("cache", "enabled"), bool):
                raise ConfigurationError(
                    "cache.enabled", self.get("cache", "enabled"), bool
                )

            # 验证验证级别
            valid_levels = ["strict", "warn", "off"]
            if self.get("validation", "level") not in valid_levels:
                raise ConfigurationError(
                    "validation.level", self.get("validation", "level"), str
                )

            # 验证日志级别
            valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
            if self.get("validation", "log_level") not in valid_log_levels:
                raise ConfigurationError(
                    "validation.log_level",
                    self.get("validation", "log_level"),
                    str
                )

            return True
        except ConfigurationError:
            raise
        except Exception as e:
            raise ConfigurationError("config.validation", str(e), str) from e
