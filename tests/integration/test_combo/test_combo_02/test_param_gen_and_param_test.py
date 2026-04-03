"""
parametrize_generator + parametrize_test 组合测试

测试 parametrize_generator 装饰器与 parametrize_test 的组合使用
探索正确的使用方式，探索不支持的使用方式并给出替代方案。

结论：@parametrize_generator 需要 (argnames, argvalues) 参数，应该使用 @param_generator 替代
"""
import pytest
from dynamic_params import parametrize_generator, parametrize_test, param_generator


# ============== 示例 01：@parametrize_generator 缺少参数 ==============

@parametrize_generator("value", [1, 2, 3])
def param_gen_basic(value):
    """基础参数化生成器 - 模块级别使用"""
    yield value


@pytest.mark.uncollected(reason="@parametrize_generator 需要 (argnames, argvalues) 参数，应该使用 @param_generator 替代")
@parametrize_test("value", param_gen_basic)
def test_param_gen_missing_args(value):
    """测试 parametrize_generator 缺少参数"""
    assert value in [1, 2, 3]


# ============== 示例 01 的推荐用法 ==============

@pytest.mark.recommended
def test_param_gen_missing_args_recommended():
    """测试 parametrize_generator 缺少参数 - 推荐版本（使用 @param_generator）"""
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


# ============== 示例 02：@parametrize_generator 与 parametrize_test 混用 ==============

@parametrize_generator("num", [10, 20, 30])
def gen_numbers(num):
    """数字生成器 - 模块级别使用"""
    yield num


@pytest.mark.uncollected(reason="@parametrize_generator 与 parametrize_test 混用会失败")
@parametrize_test("num", gen_numbers)
def test_param_gen_mixed(num):
    """测试 parametrize_generator 混用"""
    assert num in [10, 20, 30]


# ============== 示例 02 的推荐用法 ==============

@pytest.mark.recommended
def test_param_gen_mixed_recommended():
    """测试 parametrize_generator 混用 - 推荐版本（使用 @param_generator）"""
    @param_generator
    def gen_nums():
        for n in [10, 20, 30]:
            yield n
    
    @parametrize_test("num", gen_nums)
    def test(num):
        assert num in [10, 20, 30]
    
    # 手动调用
    test(10)
    test(20)
    test(30)


# ============== 示例 03：@parametrize_generator 返回值错误 ==============

@parametrize_generator("text", ["hello", "world"])
def gen_strings(text):
    """字符串生成器 - 模块级别使用"""
    yield text.upper()


@pytest.mark.uncollected(reason="@parametrize_generator 返回值错误")
@parametrize_test("text", gen_strings)
def test_param_gen_return(text):
    """测试 parametrize_generator 返回值"""
    assert text in ["hello", "world"]


# ============== 示例 03 的推荐用法 ==============

@pytest.mark.recommended
def test_param_gen_return_recommended():
    """测试 parametrize_generator 返回值 - 推荐版本（使用 @param_generator）"""
    @param_generator
    def gen_txt():
        for t in ["hello", "world"]:
            yield t.upper()
    
    @parametrize_test("text", gen_txt)
    def test(text):
        assert text in ["HELLO", "WORLD"]
    
    # 手动调用
    test("HELLO")
    test("WORLD")


# ============== 示例 04：@parametrize_generator 多参数错误 ==============

@parametrize_generator("a, b", [(1, 2), (3, 4)])
def gen_pairs(a, b):
    """多参数生成器 - 模块级别使用"""
    yield a, b


@pytest.mark.uncollected(reason="@parametrize_generator 多参数错误")
@parametrize_test("a, b", gen_pairs)
def test_param_gen_multi(a, b):
    """测试 parametrize_generator 多参数"""
    assert a in [1, 3]
    assert b in [2, 4]


# ============== 示例 04 的推荐用法 ==============

@pytest.mark.recommended
def test_param_gen_multi_recommended():
    """测试 parametrize_generator 多参数 - 推荐版本（使用 @param_generator）"""
    @param_generator
    def gen_pairs_inner():
        for pair in [(1, 2), (3, 4), (5, 6)]:
            yield pair
    
    @parametrize_test("a, b", gen_pairs_inner)
    def test(a, b):
        assert a in [1, 3, 5]
        assert b in [2, 4, 6]
    
    # 手动调用
    test(1, 2)
    test(3, 4)
    test(5, 6)
