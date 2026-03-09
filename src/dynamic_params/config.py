import os
import configparser
from typing import Dict, Any, Optional


class DynamicParamConfig:
    """动态参数化系统配置类"""
    
    DEFAULT_CONFIG = {
        "cache": {
            "enabled": "true",
            "size_function": "1000",
            "size_class": "500",
            "size_module": "200",
            "size_session": "100",
            "cleanup_interval": "100"
        },
        "validation": {
            "level": "strict",
            "log_level": "INFO"
        },
        "performance": {
            "lazy_loading": "true",
            "incremental_generation": "true"
        },
        "debug": {
            "enabled": "false",
            "profile": "false"
        }
    }
    
    def __init__(self):
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        config = configparser.ConfigParser()
        config.read_dict(self.DEFAULT_CONFIG)
        
        # 从环境变量加载
        self._update_from_env(config)
        
        # 从配置文件加载
        config_files = [
            "pytest.ini",
            "pyproject.toml",
            "dynamic_params.json",
            "dynamic_params.yaml"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                config.read(config_file)
        
        return self._normalize_config(config)
    
    def _update_from_env(self, config: configparser.ConfigParser):
        """从环境变量更新配置"""
        env_mapping = {
            "PYTEST_DYNAMIC_PARAM_CACHE": "cache.enabled",
            "PYTEST_DYNAMIC_PARAM_VALIDATION": "validation.level",
            "PYTEST_DYNAMIC_PARAM_LOG_LEVEL": "validation.log_level",
            "PYTEST_DYNAMIC_PARAM_LAZY_LOADING": "performance.lazy_loading",
            "PYTEST_DYNAMIC_PARAM_DEBUG": "debug.enabled"
        }
        
        for env_var, config_key in env_mapping.items():
            if env_var in os.environ:
                section, option = config_key.split(".")
                config[section][option] = os.environ[env_var]
    
    def _normalize_config(self, config: configparser.ConfigParser) -> Dict[str, Any]:
        """标准化配置值"""
        normalized = {}
        
        for section in config.sections():
            normalized[section] = {}
            for key, value in config[section].items():
                # 转换布尔值
                if value.lower() in ("true", "false"):
                    normalized[section][key] = config[section].getboolean(key)
                # 转换整数
                elif value.isdigit():
                    normalized[section][key] = config[section].getint(key)
                else:
                    normalized[section][key] = value
        
        return normalized
    
    def get(self, section: str, option: str, default: Optional[Any] = None) -> Any:
        """获取配置值"""
        try:
            return self._config[section][option]
        except KeyError:
            if default is not None:
                return default
            raise
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """获取整个配置节"""
        return self._config.get(section, {})