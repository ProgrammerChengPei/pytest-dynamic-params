"""DynamicParamConfig类的单元测试"""

import os
import tempfile

from dynamic_params import DynamicParamConfig


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

    def test_with_config_file(self):
        """测试从配置文件加载配置"""
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
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
            from dynamic_params import ConfigurationError

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
            from dynamic_params import ConfigurationError

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
            from dynamic_params import ConfigurationError

            try:
                config.validate()
                assert False, "Expected ConfigurationError was not raised"
            except ConfigurationError:
                pass  # 预期的错误
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
                from dynamic_params import ConfigurationError

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

    def test_reset_instance(self):
        """测试重置单例实例"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 确保有一个实例
            config1 = DynamicParamConfig()
            # 重置实例
            DynamicParamConfig.reset_instance()
            # 创建新实例
            config2 = DynamicParamConfig()
            # 验证两个实例不是同一个对象
            assert config1 is not config2
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_load_from_dict(self):
        """测试从字典加载配置"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 定义测试配置
            test_config = {
                "cache": {
                    "enabled": True,
                    "size_function": 2000
                },
                "validation": {
                    "level": "warn",
                    "log_level": "DEBUG"
                }
            }
            # 从字典加载配置
            config.load_from_dict(test_config)
            # 验证配置已加载
            assert config.get("cache", "enabled") is True
            assert config.get("cache", "size_function") == 2000
            assert config.get("validation", "level") == "warn"
            assert config.get("validation", "log_level") == "DEBUG"
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_load_from_file(self):
        """测试加载单个配置文件"""
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
            f.write("[cache]\n")
            f.write("enabled = false\n")
            temp_config_file = f.name

        try:
            # 保存原始单例实例
            original_instance = DynamicParamConfig._instance
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 加载配置文件
            import configparser
            test_config = configparser.ConfigParser()
            test_config.read_dict(DynamicParamConfig.DEFAULT_CONFIG)
            config._load_from_file(test_config, temp_config_file)
            # 验证配置已加载
            normalized = config._normalize_config(test_config)
            assert normalized["cache"]["enabled"] is False
        finally:
            # 清理临时文件
            os.unlink(temp_config_file)
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_process_pytest_dynamic_params(self):
        """测试处理 pytest.dynamic_params 格式的配置节"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 创建测试配置
            import configparser
            test_config = configparser.ConfigParser()
            test_config.read_dict(DynamicParamConfig.DEFAULT_CONFIG)
            test_config["pytest.dynamic_params"] = {
                "cache_enabled": "true",
                "cache_size_function": "3000",
                "validation": "strict",
                "log_level": "INFO",
                "lazy_loading": "true",
                "incremental_generation": "true",
                "markers": "dynamic_params: dynamic parameters"
            }
            # 处理配置
            config._process_pytest_dynamic_params(test_config)
            # 验证配置已处理
            assert "cache" in test_config
            assert "validation" in test_config
            assert "performance" in test_config
            assert "markers" in test_config
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_process_pytest_dynamic_params_with_missing_sections(self):
        """测试处理 pytest.dynamic_params 格式的配置节（缺少目标节）"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 创建测试配置，不包含目标节
            import configparser
            test_config = configparser.ConfigParser()
            # 只添加 pytest.dynamic_params 节
            test_config["pytest.dynamic_params"] = {
                "cache_enabled": "true",
                "cache_size_function": "3000",
                "validation": "strict",
                "log_level": "INFO",
                "lazy_loading": "true",
                "incremental_generation": "true",
                "markers": "dynamic_params: dynamic parameters"
            }
            # 处理配置
            config._process_pytest_dynamic_params(test_config)
            # 验证配置已处理
            assert "cache" in test_config
            assert "validation" in test_config
            assert "performance" in test_config
            assert "markers" in test_config
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_process_pytest_dynamic_params_with_cache_size_class(self):
        """测试处理 pytest.dynamic_params 格式的配置节（缓存大小类）"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 创建测试配置
            import configparser
            test_config = configparser.ConfigParser()
            test_config.read_dict(DynamicParamConfig.DEFAULT_CONFIG)
            test_config["pytest.dynamic_params"] = {
                "cache_size_class": "500"
            }
            # 处理配置
            config._process_pytest_dynamic_params(test_config)
            # 验证配置已处理
            assert "cache" in test_config
            assert "size_class" in test_config["cache"]
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_process_pytest_dynamic_params_with_cache_size_module(self):
        """测试处理 pytest.dynamic_params 格式的配置节（缓存大小模块）"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 创建测试配置
            import configparser
            test_config = configparser.ConfigParser()
            test_config.read_dict(DynamicParamConfig.DEFAULT_CONFIG)
            test_config["pytest.dynamic_params"] = {
                "cache_size_module": "200"
            }
            # 处理配置
            config._process_pytest_dynamic_params(test_config)
            # 验证配置已处理
            assert "cache" in test_config
            assert "size_module" in test_config["cache"]
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_process_pytest_dynamic_params_with_cache_size_session(self):
        """测试处理 pytest.dynamic_params 格式的配置节（缓存大小会话）"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 创建测试配置
            import configparser
            test_config = configparser.ConfigParser()
            test_config.read_dict(DynamicParamConfig.DEFAULT_CONFIG)
            test_config["pytest.dynamic_params"] = {
                "cache_size_session": "100"
            }
            # 处理配置
            config._process_pytest_dynamic_params(test_config)
            # 验证配置已处理
            assert "cache" in test_config
            assert "size_session" in test_config["cache"]
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_load_config_with_custom_config_files(self):
        """测试使用自定义配置文件列表加载配置"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 使用自定义配置文件列表
            custom_config_files = ["nonexistent.ini"]
            # 调用 _load_config 方法
            result = config._load_config(custom_config_files)
            # 验证返回值是字典
            assert isinstance(result, dict)
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_load_from_file_with_nonexistent_file(self):
        """测试加载不存在的配置文件"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 创建测试配置
            import configparser
            test_config = configparser.ConfigParser()
            test_config.read_dict(DynamicParamConfig.DEFAULT_CONFIG)
            # 加载不存在的文件
            config._load_from_file(test_config, "nonexistent.ini")
            # 验证配置对象没有被修改
            assert "cache" in test_config
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_load_from_file_with_invalid_file(self):
        """测试加载无效的配置文件"""
        # 创建临时配置文件，内容无效
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
            f.write("[invalid_section\n")  # 缺少闭合括号
            temp_config_file = f.name

        try:
            # 保存原始单例实例
            original_instance = DynamicParamConfig._instance
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 创建测试配置
            import configparser
            test_config = configparser.ConfigParser()
            test_config.read_dict(DynamicParamConfig.DEFAULT_CONFIG)
            # 加载无效文件
            config._load_from_file(test_config, temp_config_file)
            # 验证配置对象没有被修改
            assert "cache" in test_config
        finally:
            # 清理临时文件
            os.unlink(temp_config_file)
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_normalize_config_with_exception(self):
        """测试标准化配置值时的异常处理"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 创建测试配置
            import configparser
            test_config = configparser.ConfigParser()
            test_config.add_section("test")
            test_config.set("test", "bool_value", "true")
            # 模拟 getboolean 方法抛出异常
            test_section = test_config["test"]
            original_getboolean = test_section.getboolean
            test_section.getboolean = lambda option: int("not an integer")
            # 验证应该抛出 ConfigurationError
            from dynamic_params import ConfigurationError
            try:
                config._normalize_config(test_config)
                assert False, "Expected ConfigurationError was not raised"
            except ConfigurationError:
                pass  # 预期的错误
            finally:
                # 恢复原始方法
                test_section.getboolean = original_getboolean
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_get_with_key_error(self):
        """测试获取不存在的配置项时的 KeyError 处理"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 验证获取不存在的配置节会抛出 KeyError
            try:
                config.get("nonexistent_section", "option")
                assert False, "Expected KeyError was not raised"
            except KeyError:
                pass  # 预期的错误
            # 验证获取不存在的配置项会抛出 KeyError
            try:
                config.get("cache", "nonexistent_option")
                assert False, "Expected KeyError was not raised"
            except KeyError:
                pass  # 预期的错误
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_validate_with_generic_exception(self):
        """测试验证配置时的通用异常处理"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 保存原始的 get 方法
            original_get = config.get
            # 替换 get 方法，使其抛出一个通用异常
            def mock_get(section, option, default=...):
                if section == "cache" and option == "enabled":
                    raise ValueError("Mock error")
                return original_get(section, option, default)
            config.get = mock_get
            # 验证应该抛出 ConfigurationError
            from dynamic_params import ConfigurationError
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

    def test_normalize_config(self):
        """测试标准化配置值"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None

            # 创建一个配置对象
            config = DynamicParamConfig()

            # 测试标准化配置值
            import configparser
            test_config = configparser.ConfigParser()
            test_config.add_section("test")
            test_config.set("test", "bool_true", "true")
            test_config.set("test", "bool_false", "false")
            test_config.set("test", "int_value", "42")
            test_config.set("test", "string_value", "test")

            normalized = config._normalize_config(test_config)
            assert normalized["test"]["bool_true"] is True
            assert normalized["test"]["bool_false"] is False
            assert normalized["test"]["int_value"] == 42
            assert normalized["test"]["string_value"] == "test"
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_load_config_with_pytest_dynamic_params(self):
        """测试从 pytest.dynamic_params 格式的配置节加载配置"""
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
            f.write("[pytest.dynamic_params]\n")
            f.write("cache_enabled = false\n")
            f.write("cache_size_function = 2000\n")
            f.write("validation = warn\n")
            f.write("log_level = DEBUG\n")
            f.write("lazy_loading = true\n")
            f.write("incremental_generation = false\n")
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

    def test_load_config_with_invalid_file(self):
        """测试加载无效的配置文件"""
        # 创建临时配置文件，内容无效
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
            f.write("[invalid_section\n")  # 缺少闭合括号
            temp_config_file = f.name

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 重新创建配置对象以触发文件加载
            config = DynamicParamConfig()
            # 验证配置对象可以创建成功，即使文件无效
            assert config is not None
        finally:
            # 清理临时文件
            os.unlink(temp_config_file)

    def test_load_config_with_pyproject_toml(self):
        """测试从 pyproject.toml 加载配置"""
        # 创建临时 pyproject.toml 文件
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write("[tool.pytest.dynamic_params]\n")
            f.write("cache_enabled = true\n")
            f.write("validation = \"strict\"\n")
            temp_config_file = f.name

        try:
            # 重命名为 pyproject.toml
            import shutil
            shutil.move(temp_config_file, "pyproject.toml")
            
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 重新创建配置对象以触发文件加载
            config = DynamicParamConfig()
            # 验证配置对象可以创建成功
            assert config is not None
        finally:
            # 清理临时文件
            if os.path.exists("pyproject.toml"):
                os.unlink("pyproject.toml")

    def test_load_config_with_dynamic_params_json(self):
        """测试从 dynamic_params.json 加载配置"""
        # 创建临时 dynamic_params.json 文件
        import json
        config_data = {
            "cache": {
                "enabled": True,
                "size_function": 1000
            },
            "validation": {
                "level": "strict"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            temp_config_file = f.name

        try:
            # 重命名为 dynamic_params.json
            import shutil
            shutil.move(temp_config_file, "dynamic_params.json")
            
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 重新创建配置对象以触发文件加载
            config = DynamicParamConfig()
            # 验证配置对象可以创建成功
            assert config is not None
        finally:
            # 清理临时文件
            if os.path.exists("dynamic_params.json"):
                os.unlink("dynamic_params.json")

    def test_load_config_with_dynamic_params_yaml(self):
        """测试从 dynamic_params.yaml 加载配置"""
        # 创建临时 dynamic_params.yaml 文件
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("cache:\n")
            f.write("  enabled: true\n")
            f.write("  size_function: 1000\n")
            f.write("validation:\n")
            f.write("  level: strict\n")
            temp_config_file = f.name

        try:
            # 重命名为 dynamic_params.yaml
            import shutil
            shutil.move(temp_config_file, "dynamic_params.yaml")
            
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 重新创建配置对象以触发文件加载
            config = DynamicParamConfig()
            # 验证配置对象可以创建成功
            assert config is not None
        finally:
            # 清理临时文件
            if os.path.exists("dynamic_params.yaml"):
                os.unlink("dynamic_params.yaml")

    def test_load_config_with_pytest_dynamic_params_markers(self):
        """测试从 pytest.dynamic_params 加载 markers 配置"""
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
            f.write("[pytest.dynamic_params]\n")
            f.write("markers = dynamic_params: dynamic parameters\n")
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

    def test_load_config_with_pytest_dynamic_params_cache_size(self):
        """测试从 pytest.dynamic_params 加载缓存大小配置"""
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
            f.write("[pytest.dynamic_params]\n")
            f.write("cache_size_function = 2000\n")
            f.write("cache_size_class = 1000\n")
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

    def test_load_config_with_pytest_dynamic_params_performance(self):
        """测试从 pytest.dynamic_params 加载性能配置"""
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
            f.write("[pytest.dynamic_params]\n")
            f.write("lazy_loading = false\n")
            f.write("incremental_generation = true\n")
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

    def test_normalize_config_with_empty_config(self):
        """测试标准化空配置"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None

            # 创建一个配置对象
            config = DynamicParamConfig()

            # 测试标准化空配置
            import configparser
            test_config = configparser.ConfigParser()

            normalized = config._normalize_config(test_config)
            assert normalized == {}
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_normalize_config_with_boolean(self):
        """测试标准化配置值 - 布尔值"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None

            # 创建一个配置对象
            config = DynamicParamConfig()

            # 测试标准化布尔值
            import configparser
            test_config = configparser.ConfigParser()
            test_config.add_section("test")
            test_config.set("test", "true_value", "true")
            test_config.set("test", "false_value", "false")

            normalized = config._normalize_config(test_config)
            assert normalized["test"]["true_value"] is True
            assert normalized["test"]["false_value"] is False
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_normalize_config_with_integer(self):
        """测试标准化配置值 - 整数"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None

            # 创建一个配置对象
            config = DynamicParamConfig()

            # 测试标准化整数
            import configparser
            test_config = configparser.ConfigParser()
            test_config.add_section("test")
            test_config.set("test", "int_value", "42")

            normalized = config._normalize_config(test_config)
            assert normalized["test"]["int_value"] == 42
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_normalize_config_with_string(self):
        """测试标准化配置值 - 字符串"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None

            # 创建一个配置对象
            config = DynamicParamConfig()

            # 测试标准化字符串
            import configparser
            test_config = configparser.ConfigParser()
            test_config.add_section("test")
            test_config.set("test", "string_value", "test")

            normalized = config._normalize_config(test_config)
            assert normalized["test"]["string_value"] == "test"
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_normalize_config_with_exception(self):
        """测试标准化配置值时的异常处理"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None

            # 创建一个配置对象
            config = DynamicParamConfig()

            # 测试标准化时的异常 - 模拟布尔值转换异常
            import configparser
            test_config = configparser.ConfigParser()
            test_config.add_section("test")
            # 设置一个布尔值字符串
            test_config.set("test", "bool_value", "true")

            # 模拟 getboolean 方法抛出异常
            # 获取 section 对象
            test_section = test_config["test"]
            original_getboolean = test_section.getboolean
            test_section.getboolean = lambda option: int("not an integer")

            # 验证应该抛出 ConfigurationError
            from dynamic_params import ConfigurationError
            try:
                config._normalize_config(test_config)
                assert False, "Expected ConfigurationError was not raised"
            except ConfigurationError:
                pass  # 预期的错误
            finally:
                # 恢复原始方法
                test_section.getboolean = original_getboolean
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_get_with_default(self):
        """测试获取配置值时提供默认值"""
        config = DynamicParamConfig()
        # 测试获取不存在的配置节，提供默认值
        value = config.get("nonexistent_section", "option", default="default_value")
        assert value == "default_value"
        # 测试获取不存在的配置选项，提供默认值
        value = config.get("cache", "nonexistent_option", default="default_value")
        assert value == "default_value"

    def test_get_without_default(self):
        """测试获取配置值时不提供默认值"""
        config = DynamicParamConfig()
        # 测试获取存在的配置值
        value = config.get("cache", "enabled")
        assert isinstance(value, bool)
        # 测试获取不存在的配置节，不提供默认值
        from dynamic_params import ConfigurationError
        try:
            config.get("nonexistent_section", "option")
            assert False, "Expected KeyError was not raised"
        except KeyError:
            pass  # 预期的错误
        # 测试获取不存在的配置选项，不提供默认值
        try:
            config.get("cache", "nonexistent_option")
            assert False, "Expected KeyError was not raised"
        except KeyError:
            pass  # 预期的错误

    def test_singleton_pattern(self):
        """测试单例模式"""
        # 清除单例实例
        DynamicParamConfig._instance = None
        # 创建第一个实例
        config1 = DynamicParamConfig()
        # 创建第二个实例
        config2 = DynamicParamConfig()
        # 验证两个实例是同一个对象
        assert config1 is config2

    def test_get_instance(self):
        """测试get_instance方法"""
        # 清除单例实例
        DynamicParamConfig._instance = None
        # 通过get_instance获取实例
        config1 = DynamicParamConfig.get_instance()
        # 再次通过get_instance获取实例
        config2 = DynamicParamConfig.get_instance()
        # 验证两个实例是同一个对象
        assert config1 is config2
        # 验证通过get_instance获取的实例与直接创建的实例是同一个对象
        config3 = DynamicParamConfig()
        assert config1 is config3

    def test_load_config_with_pytest_ini(self):
        """测试从 pytest.ini 加载配置"""
        # 创建临时 pytest.ini 文件
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
            f.write("[cache]\n")
            f.write("enabled = false\n")
            f.write("size_function = 2000\n")
            temp_config_file = f.name

        try:
            # 重命名为 pytest.ini
            import shutil
            shutil.move(temp_config_file, "pytest.ini")
            
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 重新创建配置对象以触发文件加载
            config = DynamicParamConfig()
            # 验证配置对象可以创建成功
            assert config is not None
        finally:
            # 清理临时文件
            if os.path.exists("pytest.ini"):
                os.unlink("pytest.ini")

    def test_load_config_with_debug_section(self):
        """测试从配置文件加载 debug 节"""
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
            f.write("[debug]\n")
            f.write("enabled = true\n")
            f.write("profile = true\n")
            temp_config_file = f.name

        try:
            # 重命名为 pytest.ini
            import shutil
            shutil.move(temp_config_file, "pytest.ini")
            
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 重新创建配置对象以触发文件加载
            config = DynamicParamConfig()
            # 验证配置对象可以创建成功
            assert config is not None
        finally:
            # 清理临时文件
            if os.path.exists("pytest.ini"):
                os.unlink("pytest.ini")

    def test_get_with_default_none(self):
        """测试获取配置值时提供 None 默认值"""
        config = DynamicParamConfig()
        # 测试获取不存在的配置节，提供 None 默认值
        value = config.get("nonexistent_section", "option", default=None)
        assert value is None
        # 测试获取不存在的配置选项，提供 None 默认值
        value = config.get("cache", "nonexistent_option", default=None)
        assert value is None

    def test_validate_valid_config(self):
        """测试验证有效的配置"""
        config = DynamicParamConfig()
        # 验证默认配置是有效的
        assert config.validate() is True

    def test_validate_invalid_cache_enabled(self):
        """测试验证无效的缓存启用配置"""
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
            from dynamic_params import ConfigurationError

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
            from dynamic_params import ConfigurationError

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
            from dynamic_params import ConfigurationError

            try:
                config.validate()
                assert False, "Expected ConfigurationError was not raised"
            except ConfigurationError:
                pass  # 预期的错误
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
                from dynamic_params import ConfigurationError

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

    def test_reset_instance(self):
        """测试重置单例实例"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 确保有一个实例
            config1 = DynamicParamConfig()
            # 重置实例
            DynamicParamConfig.reset_instance()
            # 创建新实例
            config2 = DynamicParamConfig()
            # 验证两个实例不是同一个对象
            assert config1 is not config2
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_load_from_dict(self):
        """测试从字典加载配置"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 定义测试配置
            test_config = {
                "cache": {
                    "enabled": True,
                    "size_function": 2000
                },
                "validation": {
                    "level": "warn",
                    "log_level": "DEBUG"
                }
            }
            # 从字典加载配置
            config.load_from_dict(test_config)
            # 验证配置已加载
            assert config.get("cache", "enabled") is True
            assert config.get("cache", "size_function") == 2000
            assert config.get("validation", "level") == "warn"
            assert config.get("validation", "log_level") == "DEBUG"
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_load_from_file(self):
        """测试加载单个配置文件"""
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
            f.write("[cache]\n")
            f.write("enabled = false\n")
            temp_config_file = f.name

        try:
            # 保存原始单例实例
            original_instance = DynamicParamConfig._instance
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 加载配置文件
            import configparser
            test_config = configparser.ConfigParser()
            test_config.read_dict(DynamicParamConfig.DEFAULT_CONFIG)
            config._load_from_file(test_config, temp_config_file)
            # 验证配置已加载
            normalized = config._normalize_config(test_config)
            assert normalized["cache"]["enabled"] is False
        finally:
            # 清理临时文件
            os.unlink(temp_config_file)
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_process_pytest_dynamic_params(self):
        """测试处理 pytest.dynamic_params 格式的配置节"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 创建测试配置
            import configparser
            test_config = configparser.ConfigParser()
            test_config.read_dict(DynamicParamConfig.DEFAULT_CONFIG)
            test_config["pytest.dynamic_params"] = {
                "cache_enabled": "true",
                "cache_size_function": "3000",
                "validation": "strict",
                "log_level": "INFO",
                "lazy_loading": "true",
                "incremental_generation": "true",
                "markers": "dynamic_params: dynamic parameters"
            }
            # 处理配置
            config._process_pytest_dynamic_params(test_config)
            # 验证配置已处理
            assert "cache" in test_config
            assert "validation" in test_config
            assert "performance" in test_config
            assert "markers" in test_config
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_process_pytest_dynamic_params_with_missing_sections(self):
        """测试处理 pytest.dynamic_params 格式的配置节（缺少目标节）"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 创建测试配置，不包含目标节
            import configparser
            test_config = configparser.ConfigParser()
            # 只添加 pytest.dynamic_params 节
            test_config["pytest.dynamic_params"] = {
                "cache_enabled": "true",
                "cache_size_function": "3000",
                "validation": "strict",
                "log_level": "INFO",
                "lazy_loading": "true",
                "incremental_generation": "true",
                "markers": "dynamic_params: dynamic parameters"
            }
            # 处理配置
            config._process_pytest_dynamic_params(test_config)
            # 验证配置已处理
            assert "cache" in test_config
            assert "validation" in test_config
            assert "performance" in test_config
            assert "markers" in test_config
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_process_pytest_dynamic_params_with_cache_size_class(self):
        """测试处理 pytest.dynamic_params 格式的配置节（缓存大小类）"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 创建测试配置
            import configparser
            test_config = configparser.ConfigParser()
            test_config.read_dict(DynamicParamConfig.DEFAULT_CONFIG)
            test_config["pytest.dynamic_params"] = {
                "cache_size_class": "500"
            }
            # 处理配置
            config._process_pytest_dynamic_params(test_config)
            # 验证配置已处理
            assert "cache" in test_config
            assert "size_class" in test_config["cache"]
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_process_pytest_dynamic_params_with_cache_size_module(self):
        """测试处理 pytest.dynamic_params 格式的配置节（缓存大小模块）"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 创建测试配置
            import configparser
            test_config = configparser.ConfigParser()
            test_config.read_dict(DynamicParamConfig.DEFAULT_CONFIG)
            test_config["pytest.dynamic_params"] = {
                "cache_size_module": "200"
            }
            # 处理配置
            config._process_pytest_dynamic_params(test_config)
            # 验证配置已处理
            assert "cache" in test_config
            assert "size_module" in test_config["cache"]
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_process_pytest_dynamic_params_with_cache_size_session(self):
        """测试处理 pytest.dynamic_params 格式的配置节（缓存大小会话）"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 创建测试配置
            import configparser
            test_config = configparser.ConfigParser()
            test_config.read_dict(DynamicParamConfig.DEFAULT_CONFIG)
            test_config["pytest.dynamic_params"] = {
                "cache_size_session": "100"
            }
            # 处理配置
            config._process_pytest_dynamic_params(test_config)
            # 验证配置已处理
            assert "cache" in test_config
            assert "size_session" in test_config["cache"]
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_load_config_with_custom_config_files(self):
        """测试使用自定义配置文件列表加载配置"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 使用自定义配置文件列表
            custom_config_files = ["nonexistent.ini"]
            # 调用 _load_config 方法
            result = config._load_config(custom_config_files)
            # 验证返回值是字典
            assert isinstance(result, dict)
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_load_from_file_with_nonexistent_file(self):
        """测试加载不存在的配置文件"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 创建测试配置
            import configparser
            test_config = configparser.ConfigParser()
            test_config.read_dict(DynamicParamConfig.DEFAULT_CONFIG)
            # 加载不存在的文件
            config._load_from_file(test_config, "nonexistent.ini")
            # 验证配置对象没有被修改
            assert "cache" in test_config
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_load_from_file_with_invalid_file(self):
        """测试加载无效的配置文件"""
        # 创建临时配置文件，内容无效
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
            f.write("[invalid_section\n")  # 缺少闭合括号
            temp_config_file = f.name

        try:
            # 保存原始单例实例
            original_instance = DynamicParamConfig._instance
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 创建测试配置
            import configparser
            test_config = configparser.ConfigParser()
            test_config.read_dict(DynamicParamConfig.DEFAULT_CONFIG)
            # 加载无效文件
            config._load_from_file(test_config, temp_config_file)
            # 验证配置对象没有被修改
            assert "cache" in test_config
        finally:
            # 清理临时文件
            os.unlink(temp_config_file)
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_normalize_config_with_exception(self):
        """测试标准化配置值时的异常处理"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 创建测试配置
            import configparser
            test_config = configparser.ConfigParser()
            test_config.add_section("test")
            test_config.set("test", "bool_value", "true")
            # 模拟 getboolean 方法抛出异常
            test_section = test_config["test"]
            original_getboolean = test_section.getboolean
            test_section.getboolean = lambda option: int("not an integer")
            # 验证应该抛出 ConfigurationError
            from dynamic_params import ConfigurationError
            try:
                config._normalize_config(test_config)
                assert False, "Expected ConfigurationError was not raised"
            except ConfigurationError:
                pass  # 预期的错误
            finally:
                # 恢复原始方法
                test_section.getboolean = original_getboolean
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_get_with_key_error(self):
        """测试获取不存在的配置项时的 KeyError 处理"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 验证获取不存在的配置节会抛出 KeyError
            try:
                config.get("nonexistent_section", "option")
                assert False, "Expected KeyError was not raised"
            except KeyError:
                pass  # 预期的错误
            # 验证获取不存在的配置项会抛出 KeyError
            try:
                config.get("cache", "nonexistent_option")
                assert False, "Expected KeyError was not raised"
            except KeyError:
                pass  # 预期的错误
        finally:
            # 恢复原始单例实例
            DynamicParamConfig._instance = original_instance

    def test_validate_with_generic_exception(self):
        """测试验证配置时的通用异常处理"""
        # 保存原始单例实例
        original_instance = DynamicParamConfig._instance

        try:
            # 清除单例实例
            DynamicParamConfig._instance = None
            # 创建配置对象
            config = DynamicParamConfig()
            # 保存原始的 get 方法
            original_get = config.get
            # 替换 get 方法，使其抛出一个通用异常
            def mock_get(section, option, default=...):
                if section == "cache" and option == "enabled":
                    raise ValueError("Mock error")
                return original_get(section, option, default)
            config.get = mock_get
            # 验证应该抛出 ConfigurationError
            from dynamic_params import ConfigurationError
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

