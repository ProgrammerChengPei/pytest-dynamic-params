"""懒加载模块的单元测试"""

from dynamic_params.core.generator import ParamGenerator
from dynamic_params.lazy import LazyResult, generate_lazy_combinations


class TestLazyResult:
    """LazyResult类的测试类"""

    def test_initialization(self):
        """测试LazyResult初始化"""

        def dummy_func():
            return "result"

        generator = ParamGenerator(dummy_func, "test_param")
        context = {"param1": "value1"}
        cache_key = "test_key"

        lazy_result = LazyResult(generator, context, cache_key)

        assert lazy_result.generator is generator
        assert lazy_result.context == context
        assert lazy_result.cache_key == cache_key
        assert lazy_result._result is None
        assert lazy_result._executed is False

    def test_execute_once(self):
        """测试LazyResult执行一次"""
        call_count = 0

        def counting_func():
            nonlocal call_count
            call_count += 1
            return f"result_{call_count}"

        generator = ParamGenerator(counting_func, "test_param")
        context = {}
        cache_key = "test_key"

        lazy_result = LazyResult(generator, context, cache_key)

        # 第一次执行
        result1 = lazy_result.execute()
        assert result1 == "result_1"
        assert lazy_result._executed is True
        assert lazy_result._result == "result_1"

        # 第二次执行，应该返回缓存的结果
        result2 = lazy_result.execute()
        assert result2 == "result_1"
        assert call_count == 1  # 函数只应被调用一次

    def test_execute_multiple_times_returns_same_result(self):
        """测试多次执行返回相同结果"""

        def dummy_func():
            return "constant_result"

        generator = ParamGenerator(dummy_func, "test_param")
        context = {}
        cache_key = "test_key"

        lazy_result = LazyResult(generator, context, cache_key)

        result1 = lazy_result.execute()
        result2 = lazy_result.execute()
        result3 = lazy_result.execute()

        assert result1 == result2 == result3 == "constant_result"


class TestGenerateLazyCombinations:
    """generate_lazy_combinations函数的测试类"""

    def test_empty_static_params(self):
        """测试生成懒加载组合 - 空静态参数"""

        def dummy_func():
            return "result"

        generator = ParamGenerator(dummy_func, "dynamic_param")

        combinations = generate_lazy_combinations({}, [generator])

        assert len(combinations) == 1
        assert "dynamic_param" in combinations[0]
        assert isinstance(combinations[0]["dynamic_param"], LazyResult)

    def test_with_static_params(self):
        """测试生成懒加载组合 - 有静态参数"""

        def dummy_func(static_param):
            return f"result_based_on_{static_param}"

        generator = ParamGenerator(dummy_func, "dynamic_param")

        static_params = {"static_param": ["value1", "value2"]}

        combinations = generate_lazy_combinations(static_params, [generator])

        assert len(combinations) == 2

        for i, combo in enumerate(combinations):
            assert "static_param" in combo
            assert "dynamic_param" in combo
            assert isinstance(combo["dynamic_param"], LazyResult)
            # 验证context包含静态参数
            assert combo["static_param"] == static_params["static_param"][i]

    def test_multiple_generators(self):
        """测试生成懒加载组合 - 多个生成器"""

        def dummy_func1():
            return "result1"

        def dummy_func2():
            return "result2"

        generator1 = ParamGenerator(dummy_func1, "dynamic_param1")
        generator2 = ParamGenerator(dummy_func2, "dynamic_param2")

        static_params = {"static_param": ["value1"]}

        combinations = generate_lazy_combinations(
            static_params, [generator1, generator2]
        )

        assert len(combinations) == 1
        combo = combinations[0]

        assert "static_param" in combo
        assert "dynamic_param1" in combo
        assert "dynamic_param2" in combo
        assert isinstance(combo["dynamic_param1"], LazyResult)
        assert isinstance(combo["dynamic_param2"], LazyResult)

    def test_context_propagation(self):
        """测试上下文传播"""

        def context_aware_func(param1):
            return f"result_for_{param1}"

        generator = ParamGenerator(context_aware_func, "dynamic_param")

        static_params = {"param1": ["value1", "value2"]}

        combinations = generate_lazy_combinations(static_params, [generator])

        assert len(combinations) == 2

        for i, combo in enumerate(combinations):
            lazy_result = combo["dynamic_param"]
            # LazyResult的上下文应该包含静态参数
            assert lazy_result.context["param1"] == static_params["param1"][i]
