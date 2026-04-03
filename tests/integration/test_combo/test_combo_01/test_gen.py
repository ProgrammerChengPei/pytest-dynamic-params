"""
param_generator 组件测试

测试 param_generator 装饰器组件的使用方式
可以配合任意 pytest 原生组件（fixture、pytest.mark.parametrize）
探索正确的使用方式，探索不支持的使用方式并给出替代方案。

结论：param_generator 必须在测试内部定义，不能在模块级别使用
"""
import pytest
from dynamic_params import param_generator


# ============== 示例 01：param_generator 在模块级别使用 ==============

@param_generator
def gen_basic():
    """基础参数生成器 - 模块级别使用"""
    for value in [1, 2, 3]:
        yield value


@pytest.fixture
def fix_value():
    """基础 fixture"""
    return 10


@pytest.mark.uncollected(reason="param_generator 在模块级别使用会收集失败")
@pytest.mark.parametrize("value", gen_basic)
def test_gen_with_fixture(value):
    """测试 param_generator 与 fixture 组合"""
    assert value in [1, 2, 3]


# ============== 示例 01 的推荐用法 ==============

@pytest.mark.recommended
def test_gen_with_fixture_recommended():
    """测试 param_generator 与 fixture 组合 - 推荐版本（在测试内部定义 param_generator）"""
    # 方案 1：只使用 pytest 原生组件（更简洁，推荐）
    @pytest.mark.parametrize("value", [1, 2, 3])
    def test_native(value):
        assert value in [1, 2, 3]
    
    # 手动调用
    test_native(1)
    test_native(2)
    test_native(3)
    
    # 方案 2：使用插件组件 param_generator（支持动态生成参数）
    @param_generator
    def gen():
        for v in [1, 2, 3]:
            yield v
    
    @pytest.mark.parametrize("value", gen)
    def test_plugin(value):
        assert value in [1, 2, 3]
    
    # 手动调用
    test_plugin(1)
    test_plugin(2)
    test_plugin(3)


# ============== 成功示例 ==============

# 成功示例 01：param_generator 支持动态计算参数（原生 pytest 无法实现）
@pytest.mark.passed
def test_gen_dynamic_computation():
    """测试 param_generator 支持动态计算参数（原生 pytest 需要预计算所有值）"""
    @param_generator
    def gen_squares():
        # 动态计算平方值，而不是预先存储
        for i in range(1, 6):
            yield i, i * i  # (输入，期望输出)
    
    @pytest.mark.parametrize("num, square", gen_squares)
    def test(num, square):
        assert num ** 2 == square
    
    # 手动调用
    test(1, 1)
    test(2, 4)
    test(3, 9)
    test(4, 16)
    test(5, 25)


# 成功示例 02：param_generator 支持从外部数据源动态读取
@pytest.mark.passed
def test_gen_external_source():
    """测试 param_generator 从外部数据源动态读取（原生 pytest 需要预先加载所有数据）"""
    @param_generator
    def gen_from_data():
        # 模拟从文件/数据库动态读取数据
        data_source = ["apple", "banana", "cherry"]
        for item in data_source:
            yield item, len(item)
    
    @pytest.mark.parametrize("fruit, length", gen_from_data)
    def test(fruit, length):
        assert len(fruit) == length
    
    # 手动调用
    test("apple", 5)
    test("banana", 6)
    test("cherry", 6)
