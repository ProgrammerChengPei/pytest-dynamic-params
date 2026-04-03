"""
param_generator + parametrize_test 组合测试

测试 param_generator 装饰器与 parametrize_test 的组合使用
探索正确的使用方式，探索不支持的使用方式并给出替代方案。

结论：param_generator 必须在测试内部定义，不能在模块级别使用
"""
import pytest
from dynamic_params import param_generator, parametrize_test


# ============== 示例 01：param_generator 在模块级别使用 ==============

@param_generator
def gen_basic():
    """基础参数生成器 - 模块级别使用"""
    for value in [1, 2, 3]:
        yield value


@pytest.mark.uncollected(reason="param_generator 在模块级别使用会收集失败")
@parametrize_test("value", gen_basic)
def test_basic(value):
    """测试基础参数生成"""
    assert value in [1, 2, 3]


# ============== 示例 01 的推荐用法 ==============

@pytest.mark.recommended
def test_basic_recommended():
    """测试基础参数生成 - 推荐版本（在测试内部定义 param_generator）"""
    @param_generator
    def gen():
        for v in [1, 2, 3]:
            yield v
    
    @parametrize_test("value", gen)
    def test(value):
        assert value in [1, 2, 3]
    
    # 手动调用
    test(1)
    test(2)
    test(3)


# ============== 成功示例 ==============

@pytest.mark.passed
def test_multiple_params():
    """测试多参数组合"""
    @param_generator
    def gen_nums():
        for n in [10, 20, 30]:
            yield n
    
    @parametrize_test("num", gen_nums)
    @parametrize_test("mult", [1, 2, 3])
    def test(num, mult):
        assert num in [10, 20, 30]
        assert mult in [1, 2, 3]
    
    # 手动调用所有组合
    for n in [10, 20, 30]:
        for m in [1, 2, 3]:
            test(n, m)


@pytest.mark.passed
def test_strings():
    """测试字符串参数生成"""
    @param_generator
    def gen():
        for t in ["hello", "world", "test"]:
            yield t
    
    @parametrize_test("text", gen)
    def test(text):
        assert isinstance(text, str)
        assert len(text) > 0
    
    # 手动调用
    test("hello")
    test("world")
    test("test")


@pytest.mark.passed
def test_nested_lists():
    """测试嵌套列表参数生成"""
    @param_generator
    def gen():
        for lst in [[1, 2], [3, 4], [5, 6]]:
            yield lst
    
    @parametrize_test("pair", gen)
    def test(pair):
        assert isinstance(pair, list)
        assert len(pair) == 2
    
    # 手动调用
    test([1, 2])
    test([3, 4])
    test([5, 6])
