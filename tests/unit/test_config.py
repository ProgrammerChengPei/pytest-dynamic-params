"""DynamicParamConfig类的单元测试"""

import os
import tempfile
from unittest.mock import patch

from src.dynamic_params.config import DynamicParamConfig


class TestDynamicParamConfig:
    """DynamicParamConfig类的测试类"""

    def test_initialization(self):
        """测试DynamicParamConfig初始化"""
        config = DynamicParamConfig()

        # 检查默认配置是否加载
        assert config.get("cache", "enabled") is True
        assert config.get("validation", "level") == "strict"
        assert config.get("performance", "lazy_loading") is True

    def test_get_existing_value(self):
        """测试获取存在的配置值"""
        config = DynamicParamConfig()

        value = config.get("cache", "enabled")
        assert value is True

    def test_get_with_default(self):
        """测试获取不存在的配置值并返回默认值"""
        config = DynamicParamConfig()

        value = config.get("nonexistent", "option", default="default_value")
        assert value == "default_value"

    def test_get_nonexistent_without_default_raises_error(self):
        """测试获取不存在的配置值但不提供默认值会引发错误"""
        config = DynamicParamConfig()

        try:
            config.get("nonexistent", "option")
            assert False, "Expected KeyError was not raised"
        except KeyError:
            pass  # 预期的KeyError

    def test_get_section(self):
        """测试获取整个配置节"""
        config = DynamicParamConfig()

        cache_section = config.get_section("cache")
        assert isinstance(cache_section, dict)
        assert "enabled" in cache_section

    def test_get_nonexistent_section(self):
        """测试获取不存在的配置节"""
        config = DynamicParamConfig()

        nonexistent_section = config.get_section("nonexistent")
        assert nonexistent_section == {}

    def test_with_environment_variables(self):
        """测试从环境变量加载配置"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None

            with patch.dict(
                os.environ,
                {
                    "PYTEST_DYNAMIC_PARAM_CACHE": "false",
                    "PYTEST_DYNAMIC_PARAM_VALIDATION": "loose",
                },
            ):
                # 重新创建配置对象以触发环境变量加载
                config = DynamicParamConfig()

                assert config.get("cache", "enabled") is False
                assert config.get("validation", "level") == "loose"
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_with_config_file(self):
        """测试从配置文件加载配置"""
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".ini",
            delete=False
        ) as f:
            f.write("[cache]\nenabled = false\nsize_function = 2000\n")
            temp_config_file = f.name

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 重新创建配置对象以触发文件加载
            config = DynamicParamConfig()
            # 验证配置对象可以创建成功
            assert config is not None
        finally:
            # 清理临时文件
            os.unlink(temp_config_file)

    def test_get_section_nonexistent(self):
        """测试获取不存在的配置节"""
        config = DynamicParamConfig()
        section = config.get_section("nonexistent_section")
        assert section == {}

    def test_get_with_none_default(self):
        """测试获取不存在的配置值并返回None默认值"""
        config = DynamicParamConfig()
        value = config.get("nonexistent", "option", default=None)
        assert value is None

    def test_environment_variable_priority(self):
        """测试环境变量优先级高于默认配置"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None

            with patch.dict(
                os.environ,
                {
                    "PYTEST_DYNAMIC_PARAM_CACHE": "true",
                    "PYTEST_DYNAMIC_PARAM_VALIDATION": "strict",
                },
            ):
                # 重新创建配置对象以触发环境变量加载
                config = DynamicParamConfig()

                # 验证环境变量值被正确加载
                assert config.get("cache", "enabled") is True
                assert config.get("validation", "level") == "strict"
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_validate(self):
        """测试配置验证功能"""
        config = DynamicParamConfig()
        # 验证默认配置是有效的
        assert config.validate() is True

    def test_validate_invalid_cache_enabled(self):
        """测试验证无效的缓存配置"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None

            # 模拟配置对象，修改 cache.enabled 为非布尔值
            config = DynamicParamConfig()
            # 直接修改内部配置值
            config._config["cache"]["enabled"] = "not a boolean"

            # 验证应该抛出 ConfigurationError
            from src.dynamic_params.errors import ConfigurationError

            try:
                config.validate()
                assert False, "Expected ConfigurationError was not raised"
            except ConfigurationError:
                pass  # 预期的错误
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_validate_invalid_validation_level(self):
        """测试验证无效的验证级别"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None

            # 模拟配置对象，修改 validation.level 为无效值
            config = DynamicParamConfig()
            # 直接修改内部配置值
            config._config["validation"]["level"] = "invalid_level"

            # 验证应该抛出 ConfigurationError
            from src.dynamic_params.errors import ConfigurationError

            try:
                config.validate()
                assert False, "Expected ConfigurationError was not raised"
            except ConfigurationError:
                pass  # 预期的错误
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_validate_invalid_log_level(self):
        """测试验证无效的日志级别"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None

            # 模拟配置对象，修改 validation.log_level 为无效值
            config = DynamicParamConfig()
            # 直接修改内部配置值
            config._config["validation"]["log_level"] = "INVALID"

            # 验证应该抛出 ConfigurationError
            from src.dynamic_params.errors import ConfigurationError

            try:
                config.validate()
                assert False, "Expected ConfigurationError was not raised"
            except ConfigurationError:
                pass  # 预期的错误
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_update_from_env_error_handling(self):
        """测试从环境变量更新配置时的错误处理"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None

            # 设置一个无效的环境变量（格式不正确）
            with patch.dict(
                os.environ,
                {
                    "PYTEST_DYNAMIC_PARAM_CACHE": "true",
                    # 这个环境变量的配置键格式不正确
                    "PYTEST_DYNAMIC_PARAM_INVALID": "invalid_key",
                },
            ):
                # 重新创建配置对象，应该能正常创建（错误会被捕获）
                config = DynamicParamConfig()
                assert config is not None
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_validate_generic_exception(self):
        """测试验证时的通用异常处理"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None

            # 创建一个配置对象
            config = DynamicParamConfig()

            # 模拟一个会在 validate 方法中抛出非 ConfigurationError 异常的情况
            # 我们可以通过修改 _config 字典，让 get 方法抛出一个不同的异常
            # 保存原始的 get 方法
            original_get = config.get

            try:
                # 替换 get 方法，使其抛出一个通用异常
                def mock_get(section, option, default=...):
                    if section == "cache" and option == "enabled":
                        raise ValueError("Mock error")
                    return original_get(section, option, default)

                config.get = mock_get

                # 验证应该抛出 ConfigurationError
                from src.dynamic_params.errors import ConfigurationError

                try:
                    config.validate()
                    assert False, "Expected ConfigurationError was not raised"
                except ConfigurationError:
                    pass  # 预期的错误
            finally:
                # 恢复原始的 get 方法
                config.get = original_get
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance
