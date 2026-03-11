"""依赖解析模块的单元测试"""

import pytest

from dynamic_params.core.generator import ParamGenerator
from dynamic_params.dependency import CircularDependencyError, resolve_dependency_order


class TestResolveDependencyOrder:
    """resolve_dependency_order函数的测试类"""

    def test_no_dependencies(self):
        """测试无依赖的生成器排序"""

        def func_a():
            return "a"

        gen_a = ParamGenerator(func_a, "a")

        result = resolve_dependency_order([gen_a])

        assert len(result) == 1
        assert result[0].param_name == "a"

    def test_simple_chain(self):
        """测试简单依赖链"""

        def func_a():
            return "a"

        def func_b(a):
            return f"b_based_on_{a}"

        gen_a = ParamGenerator(func_a, "a")
        gen_b = ParamGenerator(func_b, "b")

        # b依赖a，所以a应该在b之前
        result = resolve_dependency_order([gen_b, gen_a])

        assert len(result) == 2
        assert result[0].param_name == "a"  # a没有依赖，应该先执行
        assert result[1].param_name == "b"  # b依赖a，应该后执行

    def test_multiple_dependencies(self):
        """测试多重依赖"""

        def func_a():
            return "a"

        def func_b():
            return "b"

        def func_c(a, b):
            return f"c_based_on_{a}_and_{b}"

        gen_a = ParamGenerator(func_a, "a")
        gen_b = ParamGenerator(func_b, "b")
        gen_c = ParamGenerator(func_c, "c")

        result = resolve_dependency_order([gen_c, gen_a, gen_b])

        # c依赖a和b，所以a和b应该在c之前
        assert result[2].param_name == "c"  # c应该在最后
        # a和b之间没有依赖关系，顺序不重要
        assert set([result[0].param_name, result[1].param_name]) == {"a", "b"}

    def test_complex_chain(self):
        """测试复杂依赖链 a->b->c"""

        def func_a():
            return "a"

        def func_b(a):
            return f"b_based_on_{a}"

        def func_c(b):
            return f"c_based_on_{b}"

        gen_a = ParamGenerator(func_a, "a")
        gen_b = ParamGenerator(func_b, "b")
        gen_c = ParamGenerator(func_c, "c")

        result = resolve_dependency_order([gen_c, gen_a, gen_b])

        # 应该是 a, b, c 的顺序
        assert result[0].param_name == "a"
        assert result[1].param_name == "b"
        assert result[2].param_name == "c"

    def test_circular_dependency_error_properties(self):
        """测试循环依赖错误的属性"""

        def func_a(b):  # a依赖b
            return f"a_based_on_{b}"

        def func_b(a):  # b依赖a - 循环依赖
            return f"b_based_on_{a}"

        gen_a = ParamGenerator(func_a, "a")
        gen_b = ParamGenerator(func_b, "b")

        # 应该抛出CircularDependencyError
        with pytest.raises(CircularDependencyError) as exc_info:
            resolve_dependency_order([gen_a, gen_b])

        error = exc_info.value
        assert hasattr(error, "cycle")
        assert error.cycle is not None
        assert len(error.cycle) >= 2


class TestCircularDependencyDetection:
    """循环依赖检测的测试类"""

    def test_circular_dependency_detection(self):
        """测试循环依赖检测"""

        def func_a(b):  # a依赖b
            return f"a_based_on_{b}"

        def func_b(a):  # b依赖a - 循环依赖
            return f"b_based_on_{a}"

        gen_a = ParamGenerator(func_a, "a")
        gen_b = ParamGenerator(func_b, "b")

        # 应该抛出CircularDependencyError
        with pytest.raises(CircularDependencyError):
            resolve_dependency_order([gen_a, gen_b])

    def test_self_dependency(self):
        """测试自依赖"""

        def func_a(a):  # a依赖自己
            return f"a_based_on_{a}"

        gen_a = ParamGenerator(func_a, "a")

        with pytest.raises(CircularDependencyError):
            resolve_dependency_order([gen_a])

    def test_circular_dependency_long_chain(self):
        """测试长链循环依赖 a->b->c->a"""

        def func_a(b):
            return f"a_based_on_{b}"

        def func_b(c):
            return f"b_based_on_{c}"

        def func_c(a):
            return f"c_based_on_{a}"

        gen_a = ParamGenerator(func_a, "a")
        gen_b = ParamGenerator(func_b, "b")
        gen_c = ParamGenerator(func_c, "c")

        with pytest.raises(CircularDependencyError):
            resolve_dependency_order([gen_a, gen_b, gen_c])
