"""懒加载模块的单元测试"""

from dynamic_params import Generator, LazyResult, generate_lazy_combinations

# 为了测试兼容性，使用 Generator 类
ParamGenerator = Generator


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
            # 验证执行结果
            assert (
                combo["dynamic_param"].execute()
                == f"result_based_on_{static_params['static_param'][i]}"
            )
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
        # 验证执行结果
        assert combo["dynamic_param1"].execute() == "result1"
        assert combo["dynamic_param2"].execute() == "result2"
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
            # 验证是LazyResult对象
            assert isinstance(lazy_result, LazyResult)
            # LazyResult的上下文应该包含静态参数
            assert lazy_result.context["param1"] == static_params["param1"][i]
            # 验证执行结果
            assert lazy_result.execute() == f"result_for_{static_params['param1'][i]}"

    def test_lazy_result_str(self):
        """测试LazyResult的__str__方法"""

        def dummy_func():
            return "result"

        generator = ParamGenerator(dummy_func, "test_param")
        context = {}
        cache_key = "test_key"

        lazy_result = LazyResult(generator, context, cache_key)
        # 未执行时的字符串表示
        str_before = str(lazy_result)
        assert "LazyResult" in str_before
        assert "dummy_func" in str_before

        # 执行后的字符串表示
        lazy_result.execute()
        str_after = str(lazy_result)
        assert str_after == "result"

    def test_lazy_result_repr(self):
        """测试LazyResult的__repr__方法"""

        def dummy_func():
            return "result"

        generator = ParamGenerator(dummy_func, "test_param")
        context = {}
        cache_key = "test_key"

        lazy_result = LazyResult(generator, context, cache_key)
        repr_str = repr(lazy_result)
        assert "LazyResult" in repr_str
        assert "dummy_func" in repr_str
        assert "executed=False" in repr_str

        lazy_result.execute()
        repr_str_after = repr(lazy_result)
        assert "executed=True" in repr_str_after

    def test_lazy_result_eq(self):
        """测试LazyResult的__eq__方法"""

        def dummy_func():
            return "result"

        generator = ParamGenerator(dummy_func, "test_param")
        context = {}
        cache_key = "test_key"

        lazy_result1 = LazyResult(generator, context, cache_key)
        lazy_result2 = LazyResult(generator, context, cache_key)
        lazy_result3 = LazyResult(generator, {"other": "value"}, cache_key)

        assert lazy_result1 == lazy_result2
        assert lazy_result1 != lazy_result3
        assert lazy_result1 != "not a LazyResult"

    def test_lazy_result_hash(self):
        """测试LazyResult的__hash__方法"""

        def dummy_func():
            return "result"

        generator = ParamGenerator(dummy_func, "test_param")
        context = {}
        cache_key = "test_key"

        lazy_result = LazyResult(generator, context, cache_key)
        # 确保可以作为字典键
        d = {lazy_result: "value"}
        assert d[lazy_result] == "value"

    def test_lazy_result_result_property(self):
        """测试LazyResult的result属性"""

        def dummy_func():
            return "result"

        generator = ParamGenerator(dummy_func, "test_param")
        context = {}
        cache_key = "test_key"

        lazy_result = LazyResult(generator, context, cache_key)
        # 通过属性获取结果
        result = lazy_result.result
        assert result == "result"
        assert lazy_result._executed is True

    def test_generate_lazy_combinations_with_context(self):
        """测试带上下文的生成懒加载组合"""

        def context_aware_func(context_param):
            return f"result_for_{context_param}"

        generator = ParamGenerator(context_aware_func, "dynamic_param")

        static_params = {"static_param": ["value1"]}
        context = {"context_param": "context_value"}

        combinations = generate_lazy_combinations(static_params, [generator], context)

        assert len(combinations) == 1
        combo = combinations[0]
        lazy_result = combo["dynamic_param"]
        # 上下文应该包含传入的上下文和静态参数
        assert lazy_result.context["context_param"] == "context_value"
        assert lazy_result.context["static_param"] == "value1"
        # 验证执行结果
        assert lazy_result.execute() == "result_for_context_value"

    def test_generate_static_combinations(self):
        """测试生成静态参数组合"""
        from dynamic_params.public.generators.lazy import _generate_static_combinations

        # 测试空参数
        empty_combinations = _generate_static_combinations({})
        assert len(empty_combinations) == 1
        assert empty_combinations[0] == {}

        # 测试单个参数
        single_param_combinations = _generate_static_combinations({"param": [1, 2, 3]})
        assert len(single_param_combinations) == 3
        assert single_param_combinations[0]["param"] == 1
        assert single_param_combinations[1]["param"] == 2
        assert single_param_combinations[2]["param"] == 3

        # 测试多个参数
        multi_param_combinations = _generate_static_combinations({"param1": [1, 2], "param2": ["a", "b"]})
        assert len(multi_param_combinations) == 4
        assert multi_param_combinations[0] == {"param1": 1, "param2": "a"}
        assert multi_param_combinations[1] == {"param1": 1, "param2": "b"}
        assert multi_param_combinations[2] == {"param1": 2, "param2": "a"}
        assert multi_param_combinations[3] == {"param1": 2, "param2": "b"}

    def test_generate_dynamic_combinations(self):
        """测试生成动态参数组合"""
        from dynamic_params.public.generators.lazy import _generate_dynamic_combinations

        def dummy_func():
            return "result"

        generator = ParamGenerator(dummy_func, "dynamic_param")

        # 测试字典类型的动态生成器
        static_combinations = [{"static": 1}, {"static": 2}]
        dynamic_generators_dict = {"dynamic": generator}
        context = {}

        combinations_dict = _generate_dynamic_combinations(static_combinations, dynamic_generators_dict, context)
        assert len(combinations_dict) == 2
        assert combinations_dict[0]["static"] == 1
        assert combinations_dict[1]["static"] == 2

        # 测试列表类型的动态生成器
        dynamic_generators_list = [generator]
        combinations_list = _generate_dynamic_combinations(static_combinations, dynamic_generators_list, context)
        assert len(combinations_list) == 2
        assert combinations_list[0]["static"] == 1
        assert combinations_list[1]["static"] == 2
        assert "dynamic_param" in combinations_list[0]

