"""
测试 dynamic_parametrize 装饰器处理器的单元测试
"""

from dynamic_params.plugin.processors.dynamic_parametrize import process_dynamic_parametrize


class TestDynamicParametrizeProcessor:
    """process_dynamic_parametrize 函数的测试类"""

    def test_process_dynamic_parametrize(self):
        """测试处理 @dynamic_parametrize 装饰器"""
        # 定义一个测试函数
        def test_func(param):
            pass
        
        # 调用处理器
        args = ("param", [1, 2, 3])
        kwargs = {}
        processed_func = process_dynamic_parametrize(test_func, args, kwargs)
        
        # 验证处理器添加的属性
        assert hasattr(processed_func, "_is_parametrized")
        assert processed_func._is_parametrized is True
        assert hasattr(processed_func, "_parametrize_info")
        assert len(processed_func._parametrize_info) == 1
        assert processed_func._parametrize_info[0]["args"] == args
        assert processed_func._parametrize_info[0]["kwargs"] == kwargs
        assert hasattr(processed_func, "pytestmark")
        assert len(processed_func.pytestmark) > 0

    def test_process_dynamic_parametrize_with_multiple_calls(self):
        """测试多次调用 process_dynamic_parametrize 函数"""
        # 定义一个测试函数
        def test_func(param1, param2):
            pass
        
        # 第一次调用处理器
        args1 = ("param1", [1, 2, 3])
        kwargs1 = {}
        processed_func = process_dynamic_parametrize(test_func, args1, kwargs1)
        
        # 第二次调用处理器
        args2 = ("param2", ["a", "b"])
        kwargs2 = {"ids": ["a_id", "b_id"]}
        processed_func = process_dynamic_parametrize(processed_func, args2, kwargs2)
        
        # 验证处理器添加的属性
        assert hasattr(processed_func, "_is_parametrized")
        assert processed_func._is_parametrized is True
        assert hasattr(processed_func, "_parametrize_info")
        assert len(processed_func._parametrize_info) == 2
        assert processed_func._parametrize_info[0]["args"] == args1
        assert processed_func._parametrize_info[0]["kwargs"] == kwargs1
        assert processed_func._parametrize_info[1]["args"] == args2
        assert processed_func._parametrize_info[1]["kwargs"] == kwargs2
        assert hasattr(processed_func, "pytestmark")
        assert len(processed_func.pytestmark) > 0
