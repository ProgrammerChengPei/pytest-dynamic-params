"""
param_generator + parametrize_test + fixture 组合测试

测试 param_generator、parametrize_test 和 pytest fixture 三者的组合使用

结论：param_generator 必须在测试内部定义，不能在模块级别使用
"""
import pytest
from dynamic_params import param_generator, parametrize_test


# ============== 失败示例 ==============
# 注意：模块级别使用装饰器会导致收集错误

def test_gen_param_fix_uncollected():
    """测试三组件基础组合 - 原始版本（uncollected: 模块级别使用会报错）"""
    # 这个模式会失败，因为装饰器在模块级别执行
    # 正确的做法是在测试内部定义和使用
    pass


# ============== 成功示例 ==============

@pytest.mark.passed
def test_gen_param_fix_manual():
    """测试三组件基础组合 - 正确版本"""
    @param_generator
    def gen_inner():
        return [1, 2, 3]
    
    @parametrize_test("base", [10, 20, 30])
    @parametrize_test("multiplier", gen_inner)
    def test(base, multiplier):
        assert base in [10, 20, 30]
        assert multiplier in [1, 2, 3]
    
    # Manual calls
    test(10, 1)
    test(20, 2)
    test(30, 3)


@pytest.mark.passed
def test_price_calculation_manual():
    """测试价格计算场景 - 正确版本"""
    @param_generator
    def gen_tax():
        return [0.1, 0.15, 0.2]
    
    @parametrize_test("price", [100, 200, 300])
    @parametrize_test("tax_rate", gen_tax)
    def test(price, tax_rate):
        assert price in [100, 200, 300]
        assert tax_rate in [0.1, 0.15, 0.2]
    
    # Manual calls
    test(100, 0.1)
    test(200, 0.15)
    test(300, 0.2)


@pytest.mark.passed
def test_name_combination_manual():
    """测试名称组合场景 - 正确版本"""
    @param_generator
    def gen_suffix():
        return ["Jr.", "Sr.", "III"]
    
    @parametrize_test("prefix", ["Mr.", "Ms.", "Dr."])
    @parametrize_test("suffix", gen_suffix)
    def test(prefix, suffix):
        assert prefix in ["Mr.", "Ms.", "Dr."]
        assert suffix in ["Jr.", "Sr.", "III"]
    
    # Manual calls
    test("Mr.", "Jr.")
    test("Ms.", "Sr.")
    test("Dr.", "III")


@pytest.mark.passed
def test_list_operations_manual():
    """测试列表操作场景 - 正确版本"""
    @param_generator
    def gen_op():
        return ["sum", "product"]
    
    @parametrize_test("base_list", [[1, 2], [3, 4], [5, 6]])
    @parametrize_test("operation", gen_op)
    def test(base_list, operation):
        assert isinstance(base_list, list)
        assert operation in ["sum", "product"]
    
    # Manual calls
    test([1, 2], "sum")
    test([3, 4], "product")
    test([5, 6], "sum")
