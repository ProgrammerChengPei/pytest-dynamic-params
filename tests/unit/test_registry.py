"""GeneratorRegistry类的单元测试"""

from dynamic_params import GeneratorRegistry, InvalidGeneratorError
from dynamic_params.public.decorators.generator import _GeneratorDecorator


class TestGeneratorRegistry:
    """GeneratorRegistry类的测试类"""

    def test_singleton(self):
        """测试Registry的单例模式"""
        registry1 = GeneratorRegistry.get_instance()
        registry2 = GeneratorRegistry.get_instance()

        assert registry1 is registry2
        assert isinstance(registry1, GeneratorRegistry)

    def test_initial_state(self):
        """测试Registry的初始状态"""
        registry = GeneratorRegistry.get_instance()

        # 初始时应该为空
        assert not registry.is_registered_by_function_name("nonexistent_func")

    def test_register_and_check(self):
        """测试注册和检查功能"""
        # 创建一个用装饰器装饰的函数
        decorator = _GeneratorDecorator()

        def dummy_func():
            return "test"

        decorated_func = decorator(dummy_func)

        registry = GeneratorRegistry.get_instance()

        # 注册装饰过的生成器函数
        registry.register(decorated_func, "test_param")

        # 检查是否已注册
        assert registry.is_registered_by_function_object(decorated_func)

    def test_is_registered_by_name(self):
        """测试按名称检查注册状态"""
        decorator = _GeneratorDecorator()

        def dummy_func():
            return "test"

        decorated_func = decorator(dummy_func)

        registry = GeneratorRegistry.get_instance()

        # 注册函数
        registry.register(decorated_func, "test_param")

        # 检查函数名是否已注册（不是参数名）
        assert registry.is_registered_by_function_name("dummy_func")

    def test_double_registration(self):
        """测试重复注册的行为"""
        decorator = _GeneratorDecorator()

        def dummy_func1():
            return "test1"

        def dummy_func2():
            return "test2"

        decorated_func1 = decorator(dummy_func1)
        decorated_func2 = decorator(dummy_func2)

        registry = GeneratorRegistry.get_instance()

        # 注册第一个函数
        registry.register(decorated_func1, "func_name")

        # 再次注册同名函数（应该替换）
        registry.register(decorated_func2, "func_name")

        # 检查是否是新的函数
        assert registry.is_registered_by_function_object(decorated_func2)

    def test_get_instance_method(self):
        """测试get_instance方法"""
        instance1 = GeneratorRegistry.get_instance()
        GeneratorRegistry()

        # 即使直接创建实例，也应该返回同一个单例
        assert GeneratorRegistry._instance is not None
        assert instance1 is GeneratorRegistry._instance

    def test_register_invalid_generator(self):
        """测试注册无效生成器（没有装饰器参数）"""

        def plain_func():
            return "plain"

        registry = GeneratorRegistry.get_instance()

        # 尝试注册一个普通函数（没有_decorator_args属性）
        try:
            registry.register(plain_func, "test_param")
            assert False, "Expected InvalidGeneratorError was not raised"
        except InvalidGeneratorError:
            pass  # 预期的错误

    def test_get_generator(self):
        """测试通过参数名获取生成器"""
        decorator = _GeneratorDecorator()

        def dummy_func():
            return "test"

        decorated_func = decorator(dummy_func)

        registry = GeneratorRegistry.get_instance()

        # 注册函数
        registry.register(decorated_func, "test_param")

        # 通过参数名获取生成器
        generator = registry.get_generator("test_param")
        assert generator is not None
        assert generator.name == "test_param"

    def test_get_generator_not_found(self):
        """测试获取不存在的生成器"""
        registry = GeneratorRegistry.get_instance()

        # 尝试获取不存在的生成器
        generator = registry.get_generator("nonexistent_param")
        assert generator is None

    def test_get_all_generators(self):
        """测试获取所有生成器"""
        decorator = _GeneratorDecorator()

        def dummy_func1():
            return "test1"

        def dummy_func2():
            return "test2"

        decorated_func1 = decorator(dummy_func1)
        decorated_func2 = decorator(dummy_func2)

        registry = GeneratorRegistry.get_instance()

        # 注册两个函数
        registry.register(decorated_func1, "test_param1")
        registry.register(decorated_func2, "test_param2")

        # 获取所有生成器
        all_generators = registry.get_all_generators()
        assert len(all_generators) >= 2  # 至少有2个

    def test_clear_cache(self):
        """测试清除缓存功能"""
        decorator = _GeneratorDecorator()

        def dummy_func():
            return "test"

        decorated_func = decorator(dummy_func)

        registry = GeneratorRegistry.get_instance()

        # 先清除缓存，确保测试环境干净
        registry.clear_cache(scope="function")

        # 注册函数
        generator = registry.register(decorated_func, "test_param")

        # 获取作用域缓存并添加一些缓存项
        scoped_cache = registry.get_scoped_cache("function")
        scoped_cache["test_key"] = "test_value"
        assert "test_key" in scoped_cache

        # 清除特定作用域的缓存
        registry.clear_cache(scope="function")

        # 检查缓存是否被清空
        scoped_cache = registry.get_scoped_cache("function")
        assert "test_key" not in scoped_cache

    def test_clear_cache_all_scopes(self):
        """测试清除所有作用域的缓存"""
        decorator = _GeneratorDecorator()

        def dummy_func():
            return "test"

        decorated_func = decorator(dummy_func)

        registry = GeneratorRegistry.get_instance()

        # 先清除所有缓存，确保测试环境干净
        registry.clear_cache()

        # 注册函数
        generator = registry.register(decorated_func, "test_param")

        # 获取作用域缓存并添加一些缓存项
        scoped_cache = registry.get_scoped_cache("function")
        scoped_cache["test_key"] = "test_value"
        assert "test_key" in scoped_cache

        # 清除所有作用域的缓存
        registry.clear_cache()

        # 检查缓存是否被清空
        scoped_cache = registry.get_scoped_cache("function")
        assert "test_key" not in scoped_cache

    def test_get_scoped_cache(self):
        """测试获取作用域缓存"""
        registry = GeneratorRegistry.get_instance()

        # 获取不同作用域的缓存
        function_cache = registry.get_scoped_cache("function")
        class_cache = registry.get_scoped_cache("class")
        module_cache = registry.get_scoped_cache("module")
        session_cache = registry.get_scoped_cache("session")

        # 验证缓存是字典类型
        assert isinstance(function_cache, dict)
        assert isinstance(class_cache, dict)
        assert isinstance(module_cache, dict)
        assert isinstance(session_cache, dict)

    def test_set_scoped_cache(self):
        """测试设置作用域缓存"""
        registry = GeneratorRegistry.get_instance()

        # 创建一个新的缓存字典
        new_cache = {"test_key": "test_value"}

        # 设置作用域缓存
        registry.set_scoped_cache("function", new_cache)

        # 验证缓存是否被正确设置
        function_cache = registry.get_scoped_cache("function")
        assert function_cache == new_cache
        assert function_cache["test_key"] == "test_value"

    def test_get_function_signature(self):
        """测试获取函数签名"""
        registry = GeneratorRegistry.get_instance()

        # 测试无参数函数
        def no_args_func():
            return "test"

        # 测试有参数函数
        def with_args_func(a, b):
            return a + b

        # 验证函数可以正常注册
        decorator = _GeneratorDecorator()
        decorated_no_args = decorator(no_args_func)
        decorated_with_args = decorator(with_args_func)

        registry.register(decorated_no_args, "no_args_param")
        registry.register(decorated_with_args, "with_args_param")

        # 验证注册成功
        assert registry.is_registered_by_function_name("no_args_func")
        assert registry.is_registered_by_function_name("with_args_func")

    def test_is_registered_by_function_name_not_found(self):
        """测试按名称检查注册状态（未找到）"""
        registry = GeneratorRegistry.get_instance()
        # 检查不存在的函数名
        assert not registry.is_registered_by_function_name("nonexistent_func")

    def test_is_registered_by_function_object_not_found(self):
        """测试按函数对象检查注册状态（未找到）"""
        registry = GeneratorRegistry.get_instance()
        # 创建一个未注册的函数
        def unregistered_func():
            return "test"
        # 检查未注册的函数对象
        assert not registry.is_registered_by_function_object(unregistered_func)

    def test_clear_cache_invalid_scope(self):
        """测试清除无效作用域的缓存"""
        registry = GeneratorRegistry.get_instance()
        # 尝试清除无效作用域的缓存，应该不会抛出异常
        registry.clear_cache(scope="invalid_scope")

    def test_set_scoped_cache_invalid_scope(self):
        """测试设置无效作用域的缓存"""
        registry = GeneratorRegistry.get_instance()
        # 尝试设置无效作用域的缓存，应该不会抛出异常
        registry.set_scoped_cache("invalid_scope", {"test_key": "test_value"})

    def test_register_with_wrapped_function(self):
        """测试注册包装函数"""
        # 创建一个装饰器
        def wrapper(func):
            def inner(*args, **kwargs):
                return func(*args, **kwargs)
            inner.__wrapped__ = func
            return inner

        # 创建并装饰函数
        decorator = _GeneratorDecorator()

        # 先使用 _GeneratorDecorator 装饰，再使用 wrapper 装饰
        @wrapper
        @decorator
        def wrapped_func():
            return "test"

        registry = GeneratorRegistry.get_instance()
        # 注册包装函数
        generator = registry.register(wrapped_func, "wrapped_param")
        # 验证注册成功
        assert generator is not None
        assert registry.is_registered_by_function_object(wrapped_func)

    def test_get_all_generators(self):
        """测试获取所有已注册的生成器"""
        # 保存原始单例实例
        original_instance = GeneratorRegistry._instance

        try:
            # 清除单例实例
            GeneratorRegistry._instance = None
            # 创建注册表实例
            registry = GeneratorRegistry.get_instance()
            # 验证初始状态下没有生成器
            generators = registry.get_all_generators()
            assert isinstance(generators, list)
            assert len(generators) == 0

            # 创建并注册一个生成器
            decorator = _GeneratorDecorator()

            @decorator
            def test_func():
                return "test"

            registry.register(test_func, "test_param")
            # 验证获取到了注册的生成器
            generators = registry.get_all_generators()
            assert len(generators) == 1
        finally:
            # 恢复原始单例实例
            GeneratorRegistry._instance = original_instance

    def test_is_registered_by_function_name_not_found(self):
        """测试通过函数名检查未注册的生成器"""
        # 保存原始单例实例
        original_instance = GeneratorRegistry._instance

        try:
            # 清除单例实例
            GeneratorRegistry._instance = None
            # 创建注册表实例
            registry = GeneratorRegistry.get_instance()
            # 验证未注册的函数名返回 False
            assert not registry.is_registered_by_function_name("nonexistent_func")
        finally:
            # 恢复原始单例实例
            GeneratorRegistry._instance = original_instance

    def test_is_registered_by_function_object_not_found(self):
        """测试通过函数对象检查未注册的生成器"""
        # 保存原始单例实例
        original_instance = GeneratorRegistry._instance

        try:
            # 清除单例实例
            GeneratorRegistry._instance = None
            # 创建注册表实例
            registry = GeneratorRegistry.get_instance()
            # 定义一个未注册的函数
            def unregistered_func():
                return "test"
            # 验证未注册的函数对象返回 False
            assert not registry.is_registered_by_function_object(unregistered_func)
        finally:
            # 恢复原始单例实例
            GeneratorRegistry._instance = original_instance

    def test_clear_cache_invalid_scope(self):
        """测试清理无效作用域的缓存"""
        # 保存原始单例实例
        original_instance = GeneratorRegistry._instance

        try:
            # 清除单例实例
            GeneratorRegistry._instance = None
            # 创建注册表实例
            registry = GeneratorRegistry.get_instance()
            # 尝试清理无效作用域的缓存（应该不会抛出异常）
            registry.clear_cache("invalid_scope")
            # 验证操作完成，没有抛出异常
            assert True
        finally:
            # 恢复原始单例实例
            GeneratorRegistry._instance = original_instance

    def test_set_scoped_cache_invalid_scope(self):
        """测试设置无效作用域的缓存"""
        # 保存原始单例实例
        original_instance = GeneratorRegistry._instance

        try:
            # 清除单例实例
            GeneratorRegistry._instance = None
            # 创建注册表实例
            registry = GeneratorRegistry.get_instance()
            # 尝试设置无效作用域的缓存（应该不会抛出异常）
            registry.set_scoped_cache("invalid_scope", {})
            # 验证操作完成，没有抛出异常
            assert True
        finally:
            # 恢复原始单例实例
            GeneratorRegistry._instance = original_instance
