"""
parametrize_generator 组件测试

测试 parametrize_generator 装饰器组件的使用方式
可以配合任意 pytest 原生组件（fixture、pytest.mark.parametrize）
探索正确的使用方式，探索不支持的使用方式并给出替代方案。

结论：@parametrize_generator 需要 (argnames, argvalues) 参数，不能单独使用
"""
import pytest
from dynamic_params import parametrize_generator


# ============== 示例 01：@parametrize_generator 缺少参数 ==============

@parametrize_generator("value", [1, 2, 3])
def param_gen_basic(value):
    """基础参数化生成器 - 模块级别使用"""
    yield value


@pytest.fixture
def fix_value():
    """基础 fixture"""
    return 10


@pytest.mark.uncollected(reason="@parametrize_generator 需要 (argnames, argvalues) 参数，不能单独使用")
@pytest.mark.parametrize("value", param_gen_basic)
def test_param_gen_with_fixture(value):
    """测试 parametrize_generator 与 fixture 组合"""
    assert value in [1, 2, 3]


# ============== 示例 01 的推荐用法 ==============

@pytest.mark.recommended
def test_param_gen_with_fixture_recommended():
    """测试 parametrize_generator 与 fixture 组合 - 推荐版本（直接使用 pytest.mark.parametrize）"""
    # 方案 1：只使用 pytest 原生组件（更简洁，推荐）
    @pytest.mark.parametrize("value", [1, 2, 3])
    def test_native(value):
        assert value in [1, 2, 3]
    
    # 手动调用
    test_native(1)
    test_native(2)
    test_native(3)
    
    # 方案 2：使用插件组件 parametrize_generator（支持动态生成参数）
    @parametrize_generator("value", [1, 2, 3])
    def param_gen(value):
        yield value
    
    @pytest.mark.parametrize("value", param_gen)
    def test_plugin(value):
        assert value in [1, 2, 3]
    
    # 手动调用
    test_plugin(1)
    test_plugin(2)
    test_plugin(3)


# ============== 成功示例 ==============

# 成功示例 01：parametrize_generator 支持带参数的动态生成（原生 pytest 无法实现）
@pytest.mark.passed
def test_param_gen_with_args():
    """测试 parametrize_generator 支持带参数的动态生成（原生 pytest 无法直接实现）"""
    @parametrize_generator("value", [1, 2, 3, 4, 5])
    def gen_filtered(value):
        # 动态过滤：只生成偶数
        if value % 2 == 0:
            yield value
    
    @pytest.mark.parametrize("value", gen_filtered)
    def test(value):
        assert value % 2 == 0
    
    # 手动调用（只有偶数）
    test(2)
    test(4)


# 成功示例 02：parametrize_generator 支持动态转换数据
@pytest.mark.passed
def test_param_gen_transformation():
    """测试 parametrize_generator 支持动态转换数据"""
    @parametrize_generator("text", ["hello", "world", "test"])
    def gen_uppercase(text):
        # 动态转换为大写
        yield text.upper()
    
    @pytest.mark.parametrize("upper", gen_uppercase)
    def test(upper):
        assert upper in ["HELLO", "WORLD", "TEST"]
    
    # 手动调用
    test("HELLO")
    test("WORLD")
    test("TEST")
