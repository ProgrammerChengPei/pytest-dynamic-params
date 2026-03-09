"""GeneratorRegistry类的单元测试"""

from src.dynamic_params.core.registry import GeneratorRegistry
from src.dynamic_params.decorators import _ParamGeneratorDecorator
from src.dynamic_params.errors import InvalidGeneratorError


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
        assert not registry.is_registered("nonexistent_func")

    def test_register_and_check(self):
        """测试注册和检查功能"""
        # 创建一个用装饰器装饰的函数
        decorator = _ParamGeneratorDecorator()
        
        def dummy_func():
            return "test"
        
        decorated_func = decorator(dummy_func)
        
        registry = GeneratorRegistry.get_instance()
        
        # 注册装饰过的生成器函数
        registered_gen = registry.register(decorated_func, "test_param")
        
        # 检查是否已注册
        assert registry.is_generator_registered(decorated_func)

    def test_is_registered_by_name(self):
        """测试按名称检查注册状态"""
        decorator = _ParamGeneratorDecorator()
        
        def dummy_func():
            return "test"
        
        decorated_func = decorator(dummy_func)
        
        registry = GeneratorRegistry.get_instance()
        
        # 注册函数
        registry.register(decorated_func, "test_param")
        
        # 检查函数名是否已注册（不是参数名）
        assert registry.is_registered("dummy_func")

    def test_double_registration(self):
        """测试重复注册的行为"""
        decorator = _ParamGeneratorDecorator()
        
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
        assert registry.is_generator_registered(decorated_func2)

    def test_get_instance_method(self):
        """测试get_instance方法"""
        instance1 = GeneratorRegistry.get_instance()
        instance2 = GeneratorRegistry()
        
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
        decorator = _ParamGeneratorDecorator()
        
        def dummy_func():
            return "test"
        
        decorated_func = decorator(dummy_func)
        
        registry = GeneratorRegistry.get_instance()
        
        # 注册函数
        registry.register(decorated_func, "test_param")
        
        # 通过参数名获取生成器
        generator = registry.get_generator("test_param")
        assert generator is not None
        assert generator.param_name == "test_param"

    def test_get_generator_not_found(self):
        """测试获取不存在的生成器"""
        registry = GeneratorRegistry.get_instance()
        
        # 尝试获取不存在的生成器
        generator = registry.get_generator("nonexistent_param")
        assert generator is None

    def test_get_all_generators(self):
        """测试获取所有生成器"""
        decorator = _ParamGeneratorDecorator()
        
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
        decorator = _ParamGeneratorDecorator()
        
        def dummy_func():
            return "test"
        
        decorated_func = decorator(dummy_func)
        
        registry = GeneratorRegistry.get_instance()
        
        # 注册函数
        generator = registry.register(decorated_func, "test_param")
        
        # 添加一些缓存项
        generator._cache["test_key"] = "test_value"
        assert len(generator._cache) == 1
        
        # 清除特定作用域的缓存
        registry.clear_cache(scope="function")
        
        # 检查缓存是否被清空
        assert len(generator._cache) == 0