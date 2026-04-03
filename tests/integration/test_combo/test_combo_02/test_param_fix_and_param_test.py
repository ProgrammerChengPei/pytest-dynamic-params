"""
parametrize_fixture + parametrize_test 组合测试

测试 parametrize_fixture 装饰器与 parametrize_test 的组合使用
探索正确的使用方式，探索不支持的使用方式并给出替代方案。

结论：@parametrize_fixture 和 @pytest.fixture 不能同时应用到同一函数，应该直接使用 @pytest.fixture(params=...)
"""
import pytest
from dynamic_params import parametrize_fixture, parametrize_test


# ============== 示例 01：@parametrize_fixture + @pytest.fixture 重复应用 ==============

@parametrize_fixture("fix_basic", [1, 2, 3])
@pytest.fixture(scope="function")
def fix_basic_impl(fix_basic):
    """基础参数化 fixture - 重复应用 fixture 装饰器"""
    return fix_basic


@pytest.mark.uncollected(reason="@parametrize_fixture 和 @pytest.fixture 不能同时应用到同一函数")
@parametrize_test("value", fix_basic_impl)
def test_fixture_duplicate(value):
    """测试 fixture 重复应用"""
    assert value in [1, 2, 3]


# ============== 示例 01 的推荐用法 ==============

@pytest.mark.recommended
def test_fixture_duplicate_recommended():
    """测试 fixture 重复应用 - 推荐版本（直接使用 @pytest.fixture(params=...)）"""
    @pytest.fixture(params=[1, 2, 3])
    def fix(request):
        return request.param
    
    @parametrize_test("value", fix)
    def test(value):
        assert value in [1, 2, 3]
    
    # 手动调用
    test(1)
    test(2)
    test(3)


# ============== 示例 02：@parametrize_fixture 单独使用（缺少 pytest.fixture） ==============

@parametrize_fixture("fix_numbers", [10, 20, 30])
def fix_numbers_impl(fix_numbers):
    """参数化 fixture - 单独使用（会收集失败）"""
    return fix_numbers


@pytest.mark.uncollected(reason="@parametrize_fixture 单独使用缺少 @pytest.fixture")
@parametrize_test("num", fix_numbers_impl)
def test_fixture_standalone(num):
    """测试 fixture 单独使用"""
    assert num in [10, 20, 30]


# ============== 示例 02 的推荐用法 ==============

@pytest.mark.recommended
def test_fixture_standalone_recommended():
    """测试 fixture 单独使用 - 推荐版本（使用 @pytest.fixture(params=...)）"""
    @pytest.fixture(params=[10, 20, 30])
    def nums(request):
        return request.param
    
    @parametrize_test("num", nums)
    def test(num):
        assert num in [10, 20, 30]
    
    # 手动调用
    test(10)
    test(20)
    test(30)


# ============== 示例 03：@parametrize_fixture 作用域设置错误 ==============

@parametrize_fixture("fix_strings", ["a", "b", "c"], scope="module")
@pytest.fixture
def fix_strings_impl(fix_strings):
    """字符串 fixture - 作用域设置冲突"""
    return fix_strings


@pytest.mark.uncollected(reason="@parametrize_fixture 作用域设置与 @pytest.fixture 冲突")
@parametrize_test("text", fix_strings_impl)
def test_fixture_scope(text):
    """测试 fixture 作用域设置"""
    assert text in ["a", "b", "c"]


# ============== 示例 03 的推荐用法 ==============

@pytest.mark.recommended
def test_fixture_scope_recommended():
    """测试 fixture 作用域设置 - 推荐版本（直接使用 @pytest.fixture(params=...)）"""
    @pytest.fixture(params=["a", "b", "c"])
    def txt(request):
        return request.param
    
    @parametrize_test("text", txt)
    def test(text):
        assert text in ["a", "b", "c"]
    
    # 手动调用
    test("a")
    test("b")
    test("c")
