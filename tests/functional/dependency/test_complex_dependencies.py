"""
测试复杂依赖链
对应需求文档中的示例9
"""

from dynamic_params import param_generator, with_dynamic_params


@param_generator
def level1():
    """第一级生成器"""
    return 1


@param_generator
def level2(level1):
    """第二级生成器，依赖level1"""
    return level1 + 1


@param_generator
def level3(level2):
    """第三级生成器，依赖level2"""
    return level2 + 1


@param_generator
def level4(level3):
    """第四级生成器，依赖level3"""
    return level3 + 1


class TestComplexDependencies:
    """测试复杂依赖链的测试类"""

    @with_dynamic_params(l1=level1, l2=level2, l3=level3, l4=level4)
    def test_deep_dependency_chain(self, l1, l2, l3, l4):
        """测试深层依赖链"""
        assert l1 == 1
        assert l2 == 2
        assert l3 == 3
        assert l4 == 4
