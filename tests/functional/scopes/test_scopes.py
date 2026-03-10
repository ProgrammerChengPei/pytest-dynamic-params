"""
测试参数生成器的不同作用域
对应需求文档中关于作用域管理的部分
"""

from dynamic_params import param_generator, with_dynamic_params


@param_generator(scope="function")
def func_scope_data():
    """函数作用域生成器"""
    return "function_data"


@param_generator(scope="class")
def class_scope_data():
    """类作用域生成器"""
    return "class_data"


@param_generator(scope="module")
def module_scope_data():
    """模块作用域生成器"""
    return "module_data"


class TestScopes:
    """测试不同作用域的测试类"""
    
    @with_dynamic_params(
        func_data=func_scope_data,
        class_data=class_scope_data,
        mod_data=module_scope_data
    )
    def test_first_function_scope(self, func_data, class_data, mod_data):
        """第一个函数作用域测试"""
        assert func_data == "function_data"
        assert class_data == "class_data"
        assert mod_data == "module_data"
    
    @with_dynamic_params(
        func_data=func_scope_data,
        class_data=class_scope_data,
        mod_data=module_scope_data
    )
    def test_second_function_scope(self, func_data, class_data, mod_data):
        """第二个函数作用域测试"""
        assert func_data == "function_data"
        assert class_data == "class_data"
        assert mod_data == "module_data"