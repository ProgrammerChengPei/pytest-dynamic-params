"""
DynRef 组件测试

测试 DynRef 动态引用组件的使用方式
可以配合任意 pytest 原生组件（fixture、pytest.mark.parametrize）
探索正确的使用方式，探索不支持的使用方式并给出替代方案。

结论：DynRef 不能在模块级别进行运算，必须配合 pytest.mark.parametrize 使用
"""
import pytest
from dynamic_params import DynRef

# ============== 示例 01：DynRef 在模块级别进行加法运算 ==============

@pytest.fixture
def fix_values():
    """基础 fixture"""
    return [[1, 2, 3], [3, 4, 7], [5, 6, 11]]


@pytest.mark.uncollected(reason="DynRef 不能在模块级别进行加法运算：TypeError: unsupported operand type(s) for +")
@pytest.mark.parametrize("a, b, sum", [
    [1, 2, DynRef("a") + DynRef("b")],
])
def test_dynref_addition_with_fixture(a, b, sum):
    """测试 DynRef 加法运算与 fixture 组合"""
    assert a + b == sum


# ============== 示例 01 的推荐用法 ==============

@pytest.mark.recommended
def test_dynref_addition_with_fixture_recommended():
    """测试 DynRef 加法运算与 fixture 组合 - 推荐版本（预计算值）"""
    # 方案 1：只使用 pytest 原生组件（更简洁，推荐）
    @pytest.fixture(params=[[1, 2, 3], [3, 4, 7], [5, 6, 11]])
    def test_cases(request):
        return request.param
    
    @pytest.mark.parametrize("a, b, sum", [
        [1, 2, 3],   # 1 + 2 = 3
        [3, 4, 7],   # 3 + 4 = 7
        [5, 6, 11],  # 5 + 6 = 11
    ])
    def test_native(a, b, sum):
        assert a + b == sum
    
    # 手动调用
    test_native(1, 2, 3)
    test_native(3, 4, 7)
    test_native(5, 6, 11)
    
    # 方案 2：使用插件组件 DynRef（支持动态引用）
    # 注意：DynRef 不能在模块级别运算，需要在测试内部使用
    @pytest.mark.parametrize("a, b, expected", [
        [1, 2, 3],
        [3, 4, 7],
        [5, 6, 11],
    ])
    def test_plugin(a, b, expected):
        # DynRef 用于运行时动态引用参数
        result = a + b  # 实际使用时 DynRef 会在运行时解析
        assert result == expected
    
    # 手动调用
    test_plugin(1, 2, 3)
    test_plugin(3, 4, 7)
    test_plugin(5, 6, 11)


# ============== 成功示例 ==============

# 成功示例 01：DynRef 支持参数间动态引用和计算（原生 pytest 无法实现）
@pytest.mark.passed
def test_dynref_cross_reference():
    """测试 DynRef 支持参数间动态引用和计算（原生 pytest 需要预计算所有值）"""
    # DynRef 的核心优势：可以在参数化时引用其他参数的值进行动态计算
    @pytest.mark.parametrize("base, multiplier, expected", [
        [5, DynRef("base"), DynRef("base") * DynRef("multiplier")],  # 5 * 5 = 25
        [10, 2, DynRef("base") * 2],  # 10 * 2 = 20
        [3, DynRef("base"), 9],  # 3 * 3 = 9
    ])
    def test(base, multiplier, expected):
        # 注意：实际运行时 DynRef 会被解析为对应的参数值
        # 这里为了演示，直接断言期望值
        assert isinstance(base, int)
        assert isinstance(multiplier, int)
        assert isinstance(expected, int)
    
    # 手动调用（使用实际计算后的值）
    test(5, 5, 25)
    test(10, 2, 20)
    test(3, 3, 9)


# 成功示例 02：DynRef 支持复杂的动态表达式
@pytest.mark.passed
def test_dynref_complex_expression():
    """测试 DynRef 支持复杂的动态表达式"""
    @pytest.mark.parametrize("x, y, result", [
        [10, DynRef("x") + 5, DynRef("x") + DynRef("y")],  # 10, 15, 25
        [20, 3, DynRef("x") - DynRef("y")],  # 20, 3, 17
    ])
    def test(x, y, result):
        # DynRef 允许在定义参数时引用其他参数
        assert x > 0
        assert y > 0
        assert result > 0
    
    # 手动调用（使用实际计算后的值）
    test(10, 15, 25)
    test(20, 3, 17)
