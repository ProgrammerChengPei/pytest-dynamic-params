"""
DynRef + parametrize_test 组合测试

测试 DynRef 动态引用与 parametrize_test 的组合使用
探索 DynRef 的正确使用方式，探索不支持的使用方式并给出替代方案。

结论：DynRef 不能在模块级别进行运算，必须在测试内部预计算值
"""
import pytest
from dynamic_params import DynRef, parametrize_test


# ============== 示例 01：DynRef 在模块级别进行加法运算 ==============

@pytest.mark.uncollected(reason="DynRef 不能在模块级别进行加法运算")
@parametrize_test("a, b, sum", [
    [1, 2, DynRef("a") + DynRef("b")],
])
def test_dynref_addition(a, b, sum):
    """测试 DynRef 加法运算"""
    assert a + b == sum


# ============== 示例 01 的推荐用法 ==============

@pytest.mark.recommended
def test_dynref_addition_recommended():
    """测试 DynRef 加法运算 - 推荐版本（在测试内部预计算值）"""
    @parametrize_test("a, b, sum", [
        [1, 2, 3],   # 1 + 2 = 3
        [3, 4, 7],   # 3 + 4 = 7
        [5, 6, 11],  # 5 + 6 = 11
    ])
    def test(a, b, sum):
        assert a + b == sum
    
    # 手动调用
    test(1, 2, 3)
    test(3, 4, 7)
    test(5, 6, 11)


# ============== 示例 02：DynRef 在模块级别进行乘法运算 ==============

@pytest.mark.uncollected(reason="DynRef 不能在模块级别进行乘法运算")
@parametrize_test("x, y, product", [
    [2, 3, DynRef("x") * DynRef("y")],
])
def test_dynref_multiplication(x, y, product):
    """测试 DynRef 乘法运算"""
    assert x * y == product


# ============== 示例 02 的推荐用法 ==============

@pytest.mark.recommended
def test_dynref_multiplication_recommended():
    """测试 DynRef 乘法运算 - 推荐版本（在测试内部预计算值）"""
    @parametrize_test("x, y, product", [
        [2, 3, 6],    # 2 * 3 = 6
        [4, 5, 20],   # 4 * 5 = 20
        [6, 7, 42],   # 6 * 7 = 42
    ])
    def test(x, y, product):
        assert x * y == product
    
    # 手动调用
    test(2, 3, 6)
    test(4, 5, 20)
    test(6, 7, 42)


# ============== 示例 03：DynRef 在模块级别进行比较运算 ==============
# 注意：DynRef 不支持比较运算符（>、<、>=、<= 等）

@pytest.mark.uncollected(reason="DynRef 不支持比较运算符：TypeError: '>' not supported between instances of 'DynRef' and 'DynRef'")
@parametrize_test("a, b, is_greater", [
    [5, 3, DynRef("a") > DynRef("b")],
])
def test_dynref_comparison(a, b, is_greater):
    """测试 DynRef 比较运算"""
    assert is_greater == (a > b)


# ============== 示例 03 的推荐用法 ==============

@pytest.mark.recommended
def test_dynref_comparison_recommended():
    """测试 DynRef 比较运算 - 推荐版本（在测试内部预计算值）"""
    @parametrize_test("a, b, is_greater", [
        [5, 3, True],   # 5 > 3
        [2, 4, False],  # 2 < 4
        [6, 6, False],  # 6 == 6
    ])
    def test(a, b, is_greater):
        assert is_greater == (a > b)
    
    # 手动调用
    test(5, 3, True)
    test(2, 4, False)
    test(6, 6, False)


# ============== 示例 04：DynRef 在模块级别进行字符串拼接 ==============

@pytest.mark.uncollected(reason="DynRef 不能在模块级别进行字符串拼接")
@parametrize_test("first, last, full", [
    ["John", "Doe", DynRef("first") + " " + DynRef("last")],
])
def test_dynref_concat(first, last, full):
    """测试 DynRef 字符串拼接"""
    assert full == f"{first} {last}"


# ============== 示例 04 的推荐用法 ==============

@pytest.mark.recommended
def test_dynref_concat_recommended():
    """测试 DynRef 字符串拼接 - 推荐版本（在测试内部预计算值）"""
    @parametrize_test("first, last, full", [
        ["John", "Doe", "John Doe"],
        ["Jane", "Smith", "Jane Smith"],
        ["Bob", "Jones", "Bob Jones"],
    ])
    def test(first, last, full):
        assert full == f"{first} {last}"
    
    # 手动调用
    test("John", "Doe", "John Doe")
    test("Jane", "Smith", "Jane Smith")
    test("Bob", "Jones", "Bob Jones")


# ============== 示例 05：DynRef 在模块级别进行复杂表达式 ==============

@pytest.mark.uncollected(reason="DynRef 不能在模块级别进行复杂表达式运算")
@parametrize_test("a, b, c, result", [
    [1, 2, 3, (DynRef("a") + DynRef("b")) * DynRef("c")],
])
def test_dynref_complex(a, b, c, result):
    """测试 DynRef 复杂表达式"""
    assert result == (a + b) * c


# ============== 示例 05 的推荐用法 ==============

@pytest.mark.recommended
def test_dynref_complex_recommended():
    """测试 DynRef 复杂表达式 - 推荐版本（在测试内部预计算值）"""
    @parametrize_test("a, b, c, result", [
        [1, 2, 3, 9],    # (1 + 2) * 3 = 9
        [2, 3, 4, 20],   # (2 + 3) * 4 = 20
        [3, 4, 5, 35],   # (3 + 4) * 5 = 35
    ])
    def test(a, b, c, result):
        assert result == (a + b) * c
    
    # 手动调用
    test(1, 2, 3, 9)
    test(2, 3, 4, 20)
    test(3, 4, 5, 35)
