"""ParamGenerator类的单元测试"""

from dynamic_params.core.generator import ParamGenerator
from dynamic_params.errors import MissingParameterError


class TestParamGenerator:
    """ParamGenerator类的测试类"""

    def test_initialization(self):
        """测试ParamGenerator初始化"""

        def dummy_func():
            return "test"

        generator = ParamGenerator(
            func=dummy_func,
            param_name="test_param",
            scope="function",
            cache_enabled=True,
            lazy_support=True,
        )

        assert generator.func == dummy_func
        assert generator.param_name == "test_param"
        assert generator.scope == "function"
        assert generator.cache_enabled is True
        assert generator.lazy_support is True
        assert generator.dependencies == []  # 无参数函数的依赖为空列表

    def test_get_result(self):
        """测试ParamGenerator的get_result方法"""

        def simple_func():
            return "result"

        generator = ParamGenerator(func=simple_func, param_name="test_param")

        result = generator.get_result({})
        assert result == "result"

    def test_with_dependencies(self):
        """测试带依赖的ParamGenerator"""

        def dependent_func(param1, param2):
            return f"{param1}_{param2}"

        generator = ParamGenerator(func=dependent_func, param_name="test_param")

        # 检查依赖提取是否正确
        expected_deps = {"param1", "param2"}
        assert set(generator.dependencies) == expected_deps

        result = generator.get_result({"param1": "hello", "param2": "world"})
        assert result == "hello_world"

    def test_caching(self):
        """测试ParamGenerator的缓存功能"""
        # 清除 GeneratorRegistry 实例，确保测试环境干净
        from dynamic_params.core.registry import GeneratorRegistry

        GeneratorRegistry._instance = None

        call_count = 0

        def counting_func():
            nonlocal call_count
            call_count += 1
            return f"result_{call_count}"

        generator = ParamGenerator(
            func=counting_func, param_name="test_param", cache_enabled=True
        )

        # 第一次调用
        result1 = generator.get_result({})
        # 触发执行
        assert str(result1) == "result_1"

        # 第二次调用，应该返回缓存结果
        result2 = generator.get_result({})
        # 触发执行
        assert str(result2) == "result_1"

        # 检查函数只被调用了一次
        assert call_count == 1

    def test_stats(self):
        """测试ParamGenerator的统计信息"""
        # 清除 GeneratorRegistry 实例，确保测试环境干净
        from dynamic_params.core.registry import GeneratorRegistry

        GeneratorRegistry._instance = None

        def simple_func():
            return "result"

        generator = ParamGenerator(
            func=simple_func, param_name="test_param", cache_enabled=True
        )

        # 初始统计
        assert generator.stats["hits"] == 0
        assert generator.stats["misses"] == 0
        assert generator.stats["executions"] == 0

        # 第一次调用
        result1 = generator.get_result({})
        # 触发执行
        _ = str(result1)
        assert generator.stats["misses"] == 1
        assert generator.stats["executions"] == 1

        # 第二次调用（命中缓存）
        result2 = generator.get_result({})
        # 触发执行
        _ = str(result2)
        assert generator.stats["hits"] == 1
        assert generator.stats["misses"] == 1
        assert generator.stats["executions"] == 1

    def test_cache_disabled(self):
        """测试禁用缓存时的行为"""
        call_count = 0

        def counting_func():
            nonlocal call_count
            call_count += 1
            return f"result_{call_count}"

        generator = ParamGenerator(
            func=counting_func, param_name="test_param", cache_enabled=False
        )

        # 多次调用，每次都应执行函数
        result1 = generator.get_result({})
        result2 = generator.get_result({})

        assert result1 == "result_1"
        assert result2 == "result_2"
        assert call_count == 2

    def test_get_result_without_lazy_support(self):
        """测试不支持懒加载时的get_result方法"""
        # 清除 GeneratorRegistry 实例，确保测试环境干净
        from dynamic_params.core.registry import GeneratorRegistry

        GeneratorRegistry._instance = None

        def simple_func():
            return "result"

        generator = ParamGenerator(
            func=simple_func,
            param_name="test_param",
            lazy_support=False,  # 不支持懒加载
        )

        result = generator.get_result({})
        assert result == "result"

    def test_missing_parameter_error(self):
        """测试缺少参数时的错误"""

        def dependent_func(param1, param2):
            return f"{param1}_{param2}"

        generator = ParamGenerator(func=dependent_func, param_name="test_param")

        # 尝试调用时不提供所需参数，应该抛出MissingParameterError
        try:
            result = generator.get_result({"param1": "hello"})  # 缺少param2
            # 触发执行，应该抛出异常
            _ = str(result)
            assert False, "Expected MissingParameterError was not raised"
        except MissingParameterError as e:
            assert e.param_name == "param2"
            assert e.generator_name == "dependent_func"
            assert "param1" in e.available_params
            assert "param2" in e.required_params

    def test_register_input_values(self):
        """测试注册输入值"""

        def simple_func():
            return "result"

        generator = ParamGenerator(func=simple_func, param_name="test_param")

        # 注册输入值
        test_values = ["value1", "value2", "value3"]
        generator.register_input_values(test_values)

        # 检查值是否被正确注册
        assert generator._input_values == test_values
