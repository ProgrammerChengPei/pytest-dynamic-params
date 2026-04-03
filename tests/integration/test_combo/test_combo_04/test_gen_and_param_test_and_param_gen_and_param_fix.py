"""
param_generator + parametrize_test + parametrize_generator + parametrize_fixture 组合测试

测试四个组件的组合使用
"""
import pytest
from dynamic_params import param_generator, parametrize_test, parametrize_generator, parametrize_fixture


# ============== 基础四组件测试 ==============

@parametrize_fixture("fix_base", [10, 20, 30])
@pytest.fixture(scope="function")
def fix_base_impl(fix_base):
    """基础参数化 fixture"""
    return fix_base


@parametrize_generator
def param_gen_multiplier():
    """乘数参数化生成器"""
    for multiplier in [1, 2, 3]:
        yield multiplier


@param_generator
def gen_offset():
    """生成偏移量"""
    return [0, 5, 10]


@parametrize_test("base", fix_base_impl)
@parametrize_test("multiplier", param_gen_multiplier)
@parametrize_test("offset", gen_offset)
@pytest.mark.success
def test_four_components_basic(base, multiplier, offset):
    """测试四组件基础组合"""
    assert base in [10, 20, 30]
    assert multiplier in [1, 2, 3]
    assert offset in [0, 5, 10]


# ============== 计算场景测试 ==============

@parametrize_fixture("fix_price", [100, 200, 300])
@pytest.fixture(scope="function")
def fix_price_impl(fix_price):
    """价格参数化 fixture"""
    return fix_price


@parametrize_generator
def param_gen_tax_rate():
    """税率参数化生成器"""
    for tax_rate in [0.1, 0.15, 0.2]:
        yield tax_rate


@param_generator
def gen_discount():
    """生成折扣"""
    return [0, 0.05, 0.1]


@parametrize_test("price", fix_price_impl)
@parametrize_test("tax_rate", param_gen_tax_rate)
@parametrize_test("discount", gen_discount)
@pytest.mark.success
def test_price_calculation(price, tax_rate, discount):
    """测试价格计算场景"""
    assert price in [100, 200, 300]
    assert tax_rate in [0.1, 0.15, 0.2]
    assert discount in [0, 0.05, 0.1]


# ============== 字符串处理场景 ==============

@parametrize_fixture("fix_prefix", ["Mr.", "Ms.", "Dr."])
@pytest.fixture(scope="function")
def fix_prefix_impl(fix_prefix):
    """前缀参数化 fixture"""
    return fix_prefix


@parametrize_generator
def param_gen_middle():
    """中间名参数化生成器"""
    for middle in ["A.", "B.", "C."]:
        yield middle


@param_generator
def gen_suffix():
    """生成后缀"""
    return ["Jr.", "Sr.", "III"]


@parametrize_test("prefix", fix_prefix_impl)
@parametrize_test("middle", param_gen_middle)
@parametrize_test("suffix", gen_suffix)
@pytest.mark.success
def test_name_combination(prefix, middle, suffix):
    """测试名称组合场景"""
    assert prefix in ["Mr.", "Ms.", "Dr."]
    assert middle in ["A.", "B.", "C."]
    assert suffix in ["Jr.", "Sr.", "III"]


# ============== 列表操作场景 ==============

@parametrize_fixture("fix_base_list", [[1, 2], [3, 4], [5, 6]])
@pytest.fixture(scope="function")
def fix_base_list_impl(fix_base_list):
    """基础列表参数化 fixture"""
    return fix_base_list


@parametrize_generator
def param_gen_operation():
    """操作参数化生成器"""
    for operation in ["sum", "product", "concat"]:
        yield operation


@param_generator
def gen_format_type():
    """生成格式类型"""
    return ["list", "tuple", "string"]


@parametrize_test("base_list", fix_base_list_impl)
@parametrize_test("operation", param_gen_operation)
@parametrize_test("format_type", gen_format_type)
@pytest.mark.success
def test_list_operations(base_list, operation, format_type):
    """测试列表操作场景"""
    assert isinstance(base_list, list)
    assert operation in ["sum", "product", "concat"]
    assert format_type in ["list", "tuple", "string"]


# ============== 边界条件场景 ==============

@parametrize_fixture("fix_boundary", [0, -1, 100])
@pytest.fixture(scope="function")
def fix_boundary_impl(fix_boundary):
    """边界值参数化 fixture"""
    return fix_boundary


@parametrize_generator
def param_gen_check_type():
    """检查类型参数化生成器"""
    for check_type in ["is_zero", "is_negative", "is_positive"]:
        yield check_type


@param_generator
def gen_tolerance():
    """生成容差"""
    return [0.001, 0.01, 0.1]


@parametrize_test("boundary", fix_boundary_impl)
@parametrize_test("check_type", param_gen_check_type)
@parametrize_test("tolerance", gen_tolerance)
@pytest.mark.success
def test_boundary_conditions(boundary, check_type, tolerance):
    """测试边界条件场景"""
    assert boundary in [0, -1, 100]
    assert check_type in ["is_zero", "is_negative", "is_positive"]
    assert tolerance in [0.001, 0.01, 0.1]


# ============== 失败测试用例 ==============

@parametrize_fixture("fix_error_base", [1, 2, 3])
@pytest.fixture(scope="function")
def fix_error_base_impl(fix_error_base):
    """错误基础值参数化 fixture"""
    return fix_error_base


@parametrize_generator
def param_gen_error_multiplier():
    """错误乘数参数化生成器"""
    for multiplier in [0, 1, 2]:
        yield multiplier


@param_generator
def gen_error_offset():
    """错误偏移量生成器"""
    return [100, 200, 300]


@parametrize_test("base", fix_error_base_impl)
@parametrize_test("multiplier", param_gen_error_multiplier)
@parametrize_test("offset", gen_error_offset)
@pytest.mark.error
def test_error_case(base, multiplier, offset):
    """测试错误情况（预期失败）"""
    # 这个测试预期会失败
    assert base * multiplier + offset == 1000  # 永远不会成立
