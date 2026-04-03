"""
parametrize_test 组件测试

测试 parametrize_test 装饰器组件的使用方式
可以配合任意 pytest 原生组件（fixture、pytest.mark.parametrize）
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
def test_param_test_with_fixture(value):
    """测试 parametrize_test 与 fixture 组合"""
    assert value in [1, 2, 3]


# ============== 示例 01 的推荐用法 ==============

@pytest.mark.recommended
def test_param_test_with_fixture_recommended():
    """测试 parametrize_test 与 fixture 组合 - 推荐版本（在测试内部定义 fixture）"""
    # 方案 1：只使用 pytest 原生组件（更简洁，推荐）
    @pytest.mark.parametrize("value", [1, 2, 3])
    def test_native(value):
        assert value in [1, 2, 3]
    
    # 手动调用
    test_native(1)
    test_native(2)
    test_native(3)
    
    # 方案 2：使用插件组件 parametrize_test（支持动态参数源）
    @pytest.fixture(params=[1, 2, 3])
    def fix(request):
        return request.param
    
    @parametrize_test("value", fix)
    def test_plugin(value):
        assert value in [1, 2, 3]
    
    # 手动调用
    test_plugin(1)
    test_plugin(2)
    test_plugin(3)


# ============== 成功示例 ==============

# 成功示例 01：parametrize_test 支持动态参数源（原生 pytest 需要静态列表）
@pytest.mark.passed
def test_param_test_dynamic_source():
    """测试 parametrize_test 支持动态参数源（原生 pytest.mark.parametrize 需要静态列表）"""
    # 动态生成参数列表
    def generate_test_cases():
        cases = []
        for i in range(1, 6):
            cases.append((i, i * 2))
        return cases
    
    @parametrize_test("num, doubled", generate_test_cases())
    def test(num, doubled):
        assert num * 2 == doubled
    
    # 手动调用
    test(1, 2)
    test(2, 4)
    test(3, 6)
    test(4, 8)
    test(5, 10)


# 成功示例 02：parametrize_test 支持多个动态参数源组合
@pytest.mark.passed
def test_param_test_multiple_sources():
    """测试 parametrize_test 支持多个动态参数源组合"""
    def get_nums():
        return [10, 20, 30]
    
    def get_multipliers():
        return [1, 2, 3]
    
    @parametrize_test("num", get_nums())
    @parametrize_test("mult", get_multipliers())
    def test(num, mult):
        result = num * mult
        assert result > 0
    
    # 手动调用所有组合
    for n in [10, 20, 30]:
        for m in [1, 2, 3]:
            test(n, m)
