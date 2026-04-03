"""
fixture + parametrize_test 组合测试

测试 pytest fixture 与 parametrize_test 的组合使用
探索正确的使用方式，探索不支持的使用方式并给出替代方案。

结论：fixture 可以在模块级别定义，parametrize_test 必须在测试内部使用
"""
import pytest
from dynamic_params import parametrize_test


# ============== 示例 01：fixture 在模块级别使用 ==============

@pytest.fixture
def fix_basic():
    """基础 fixture - 模块级别使用"""
    return [1, 2, 3]


@pytest.mark.uncollected(reason="fixture 在模块级别使用，parametrize_test 无法正确收集")
@parametrize_test("value", fix_basic)
def test_basic_fixture(value):
    """测试基础 fixture 参数化"""
    assert value in [1, 2, 3]


# ============== 示例 01 的推荐用法 ==============

@pytest.mark.recommended
def test_basic_fixture_recommended():
    """测试基础 fixture 参数化 - 推荐版本（在测试内部定义 fixture）"""
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


# ============== 成功示例 ==============

@pytest.mark.passed
def test_multiple_fixtures():
    """测试多个 fixture 组合"""
    @pytest.fixture(params=[10, 20, 30])
    def nums(request):
        return request.param
    
    @pytest.fixture(params=[1, 2, 3])
    def mults(request):
        return request.param
    
    @parametrize_test("num", nums)
    @parametrize_test("mult", mults)
    def test(num, mult):
        assert num in [10, 20, 30]
        assert mult in [1, 2, 3]
    
    # 手动调用所有组合
    for n in [10, 20, 30]:
        for m in [1, 2, 3]:
            test(n, m)


@pytest.mark.passed
def test_string_fixture():
    """测试字符串 fixture"""
    @pytest.fixture(params=["hello", "world", "test"])
    def txt(request):
        return request.param
    
    @parametrize_test("text", txt)
    def test(text):
        assert isinstance(text, str)
        assert len(text) > 0
    
    # 手动调用
    test("hello")
    test("world")
    test("test")


@pytest.mark.passed
def test_dict_fixture():
    """测试字典 fixture"""
    @pytest.fixture(params=[{"a": 1}, {"b": 2}, {"c": 3}])
    def dct(request):
        return request.param
    
    @parametrize_test("data", dct)
    def test(data):
        assert isinstance(data, dict)
        assert len(data) == 1
    
    # 手动调用
    test({"a": 1})
    test({"b": 2})
    test({"c": 3})
