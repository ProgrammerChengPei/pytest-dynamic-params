import pytest


def test_pytest_native_functionality():
    """测试pytest原生功能的基础用法"""
    
    # 测试简单的参数化
    @pytest.mark.parametrize("value", [1, 2, 3])
    def test_simple_param(value):
        assert value in [1, 2, 3]
    
    # 手动测试
    test_simple_param(1)
    test_simple_param(2)
    test_simple_param(3)


@pytest.fixture
def fix_a():
    return "a"

@pytest.fixture  
def fix_ab(fix_a):
    return fix_a + "b"


def test_fixture_nesting(fix_ab):
    """测试pytest原生fixture嵌套功能"""
    assert fix_ab == "ab"


def test_pytest_parametrize_static():
    """测试pytest.mark.parametrize的静态参数化功能"""
    
    @pytest.mark.parametrize("x,y,expected", [
        (1, 1, 2),
        (2, 3, 5), 
        (10, 20, 30)
    ])
    def test_addition(x, y, expected):
        assert x + y == expected
    
    # 验证测试用例
    test_addition(1, 1, 2)
    test_addition(2, 3, 5)
    test_addition(10, 20, 30)
