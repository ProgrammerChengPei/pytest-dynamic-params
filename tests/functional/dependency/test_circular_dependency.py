"""测试循环依赖检测功能"""

import pytest

from dynamic_params import ParamGenerator, param_generator
from dynamic_params.dependency import (
    CircularDependencyError,
    resolve_dependency_order,
)


def test_circular_dependency_detection():
    """测试循环依赖检测功能"""

    @param_generator
    def generate_a(b):
        return f"a_from_{b}"

    @param_generator
    def generate_b(a):
        return f"b_from_{a}"

    # 创建参数生成器实例
    gen_a = ParamGenerator(func=generate_a, param_name="a")
    gen_b = ParamGenerator(func=generate_b, param_name="b")

    # 尝试解析具有循环依赖的生成器，应该抛出异常
    with pytest.raises(CircularDependencyError):
        resolve_dependency_order([gen_a, gen_b])


def test_non_circular_dependency():
    """测试非循环依赖能够正确解析"""

    @param_generator
    def generate_a():
        return "value_a"

    @param_generator
    def generate_b(a):
        return f"b_from_{a}"

    # 创建参数生成器实例
    gen_a = ParamGenerator(func=generate_a, param_name="a")
    gen_b = ParamGenerator(func=generate_b, param_name="b")

    # 解析依赖顺序，不应该抛出异常
    ordered = resolve_dependency_order([gen_b, gen_a])

    # 验证依赖顺序正确（a应该在b之前）
    param_names = [gen.param_name for gen in ordered]
    assert param_names.index("a") < param_names.index("b")


if __name__ == "__main__":
    test_circular_dependency_detection()
    test_non_circular_dependency()
    print("所有循环依赖检测测试通过!")
