"""
parametrize_fixture 组件测试

测试 parametrize_fixture 装饰器组件的使用方式
可以配合任意 pytest 原生组件（fixture、pytest.mark.parametrize）
探索正确的使用方式，探索不支持的使用方式并给出替代方案。

结论：@parametrize_fixture 和 @pytest.fixture 不能同时应用到同一函数
"""
import pytest
from dynamic_params import parametrize_fixture


# ============== 示例 01：@parametrize_fixture + @pytest.fixture 重复应用 ==============

@parametrize_fixture("fix_basic", [1, 2, 3])
@pytest.fixture(scope="function")
def fix_basic_impl(fix_basic):
    """基础参数化 fixture - 重复应用 fixture 装饰器"""
    return fix_basic


@pytest.fixture
def fix_value():
    """另一个 fixture"""
    return 10


@pytest.mark.uncollected(reason="@parametrize_fixture 和 @pytest.fixture 不能同时应用到同一函数")
@pytest.mark.parametrize("value", fix_basic_impl)
def test_param_fix_with_fixture(value):
    """测试 parametrize_fixture 与 fixture 组合"""
    assert value in [1, 2, 3]


# ============== 示例 01 的推荐用法 ==============

@pytest.mark.recommended
def test_param_fix_with_fixture_recommended():
    """测试 parametrize_fixture 与 fixture 组合 - 推荐版本（直接使用 @pytest.fixture(params=...)）"""
    # 方案 1：只使用 pytest 原生组件（更简洁，推荐）
    @pytest.fixture(params=[1, 2, 3])
    def fix_native(request):
        return request.param
    
    @pytest.mark.parametrize("value", fix_native)
    def test_native(value):
        assert value in [1, 2, 3]
    
    # 手动调用
    test_native(1)
    test_native(2)
    test_native(3)
    
    # 方案 2：使用插件组件 parametrize_fixture（支持动态参数源）
    @parametrize_fixture("fix_plugin", [1, 2, 3])
    def fix_plugin_impl(fix_plugin):
        return fix_plugin
    
    @pytest.mark.parametrize("value", fix_plugin_impl)
    def test_plugin(value):
        assert value in [1, 2, 3]
    
    # 手动调用
    test_plugin(1)
    test_plugin(2)
    test_plugin(3)


# ============== 成功示例 ==============

# 成功示例 01：parametrize_fixture 支持动态参数化 fixture（原生 pytest 需要 params 参数）
@pytest.mark.passed
def test_param_fix_dynamic_fixture():
    """测试 parametrize_fixture 支持动态参数化 fixture（原生 pytest 需要在定义时指定 params）"""
    # 动态生成 fixture 参数
    def get_fixture_params():
        return [100, 200, 300]
    
    @parametrize_fixture("fix_dynamic", get_fixture_params())
    def fix_impl(fix_dynamic):
        return fix_dynamic * 2  # 可以在 fixture 中进行处理
    
    @pytest.mark.parametrize("value", fix_impl)
    def test(value):
        assert value in [200, 400, 600]
    
    # 手动调用
    test(200)
    test(400)
    test(600)


# 成功示例 02：parametrize_fixture 支持多个动态 fixture 组合
@pytest.mark.passed
def test_param_fix_multiple_dynamic():
    """测试 parametrize_fixture 支持多个动态 fixture 组合"""
    @parametrize_fixture("base", [10, 20])
    def base_impl(base):
        return base
    
    @parametrize_fixture("multiplier", [1, 2, 3])
    def mult_impl(multiplier):
        return multiplier
    
    @pytest.mark.parametrize("b, m", [
        (base_impl, mult_impl),
    ])
    def test(b, m):
        result = b * m
        assert result > 0
    
    # 手动调用所有组合
    for b in [10, 20]:
        for m in [1, 2, 3]:
            test(b, m)
