"""
使用pytest-benchmark的基准测试
"""

import pytest

from src.dynamic_params import param_generator, with_dynamic_params


class TestBenchmark:
    """使用pytest-benchmark的基准测试类"""
    
    def test_simple_generator_benchmark(self, benchmark):
        """测试简单生成器的性能基准"""
        @param_generator
        def simple_gen(x):
            return x + 1
        
        @with_dynamic_params(result=simple_gen)
        def test_func(x, result):
            assert result == x + 1
        
        # 使用benchmark装饰器测量性能
        benchmark(lambda x: test_func(x, x + 1), 42)
    
    def test_multiple_generators_benchmark(self, benchmark):
        """测试多个生成器的性能基准"""
        @param_generator
        def gen1(x):
            return x * 2
        
        @param_generator
        def gen2(x):
            return x + 10
        
        @with_dynamic_params(doubled=gen1, added=gen2)
        def test_func(x, doubled, added):
            assert doubled == x * 2
            assert added == x + 10
        
        benchmark(lambda x: test_func(x, x * 2, x + 10), 42)
    
    def test_cached_generator_benchmark(self, benchmark):
        """测试带缓存的生成器性能基准"""
        @param_generator(cache=True)
        def cached_gen(x):
            # 模拟一些计算
            result = 0
            for i in range(10):
                result += x * i
            return result
        
        @with_dynamic_params(result=cached_gen)
        def test_func(x, result):
            expected = sum(x * i for i in range(10))
            assert result == expected
        
        benchmark(lambda x: test_func(x, sum(x * i for i in range(10))), 42)
    
    def test_nested_generators_benchmark(self, benchmark):
        """测试嵌套生成器的性能基准"""
        @param_generator
        def base_gen(x):
            return x + 5
        
        @param_generator
        def derived_gen(base):
            return base * 3
        
        @with_dynamic_params(base=base_gen, derived=derived_gen)
        def test_func(x, base, derived):
            assert base == x + 5
            assert derived == (x + 5) * 3
        
        benchmark(lambda x: test_func(x, x + 5, (x + 5) * 3), 42)
    
    def test_different_parameter_types_benchmark(self, benchmark):
        """测试不同类型参数的性能基准"""
        @param_generator
        def process_string(s):
            return s.upper()
        
        @with_dynamic_params(uppercase=process_string)
        def test_func(s, uppercase):
            assert uppercase == s.upper()
        
        benchmark(lambda s: test_func(s, s.upper()), "test_string")
