import configparser
import os
from typing import Any, Dict, Optional

from .errors import ConfigurationError


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
        "performance": {"lazy_loading": "true", "incremental_generation": "true"},
        "debug": {"enabled": "false", "profile": "false"},
    }

    _instance = None

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

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        config = configparser.ConfigParser()
        config.read_dict(self.DEFAULT_CONFIG)

        # 从配置文件加载（优先级：pytest.ini > pyproject.toml > dynamic_params.json/yaml）
        config_files = [
            "pytest.ini",
            "pyproject.toml",
            "dynamic_params.json",
            "dynamic_params.yaml",
        ]

        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    config.read(config_file)
                except Exception as e:
                    print(f"Warning: Failed to read {config_file}: {e}")

        # 从环境变量加载（优先级最高）
        self._update_from_env(config)

        return self._normalize_config(config)

    def _update_from_env(self, config: configparser.ConfigParser):
        """从环境变量更新配置"""
        env_mapping = {
            "PYTEST_DYNAMIC_PARAM_CACHE": "cache.enabled",
            "PYTEST_DYNAMIC_PARAM_VALIDATION": "validation.level",
            "PYTEST_DYNAMIC_PARAM_LOG_LEVEL": "validation.log_level",
            "PYTEST_DYNAMIC_PARAM_LAZY_LOADING": "performance.lazy_loading",
            "PYTEST_DYNAMIC_PARAM_INCREMENTAL": "performance.incremental_generation",
            "PYTEST_DYNAMIC_PARAM_DEBUG": "debug.enabled",
            "PYTEST_DYNAMIC_PARAM_PROFILE": "debug.profile",
            "PYTEST_DYNAMIC_PARAM_CACHE_DIR": "cache.dir",
        }

        for env_var, config_key in env_mapping.items():
            if env_var in os.environ:
                try:
                    section, option = config_key.split(".")
                    if section not in config:
                        config[section] = {}
                    config[section][option] = os.environ[env_var]
                except Exception as e:
                    print(f"Warning: Failed to update config from {env_var}: {e}")

    def _normalize_config(self, config: configparser.ConfigParser) -> Dict[str, Any]:
        """标准化配置值"""
        normalized = {}

        for section in config.sections():
            normalized[section] = {}
            for key, value in config[section].items():
                try:
                    # 转换布尔值
                    if value.lower() in ("true", "false"):
                        normalized[section][key] = config[section].getboolean(key)
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

    def get(self, section: str, option: str, default: Optional[Any] = ...) -> Any:
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
                    "validation.log_level", self.get("validation", "log_level"), str
                )

            return True
        except ConfigurationError:
            raise
        except Exception as e:
            raise ConfigurationError("config.validation", str(e), str) from e
