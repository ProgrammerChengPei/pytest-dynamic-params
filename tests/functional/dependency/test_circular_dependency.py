"""测试循环依赖检测功能"""

import pytest

from dynamic_params import (
    CircularDependencyError,
    Generator,
    generator,
    resolve_dependency_order,
)

# 为了测试兼容性，使用 Generator 类
ParamGenerator = Generator


def test_circular_dependency_detection():
    """测试循环依赖检测功能"""

    @generator
    def generate_a(b):
        return f"a_from_{b}"

    @generator
    def generate_b(a):
        return f"b_from_{a}"

    # 创建参数生成器实例
    gen_a = ParamGenerator(func=generate_a, name="a")
    gen_b = ParamGenerator(func=generate_b, name="b")

    # 尝试解析具有循环依赖的生成器，应该抛出异常
    with pytest.raises(CircularDependencyError):
        resolve_dependency_order([gen_a, gen_b])


def test_non_circular_dependency():
    """测试非循环依赖能够正确解析"""

    @generator
    def generate_a():
        return "value_a"

    @generator
    def generate_b(a):
        return f"b_from_{a}"

    # 创建参数生成器实例
    gen_a = ParamGenerator(func=generate_a, name="a")
    gen_b = ParamGenerator(func=generate_b, name="b")

    # 解析依赖顺序，不应该抛出异常
    ordered = resolve_dependency_order([gen_b, gen_a])

    # 验证依赖顺序正确（a应该在b之前）
    param_names = [gen.name for gen in ordered]
    assert param_names.index("a") < param_names.index("b")


if __name__ == "__main__":
    test_circular_dependency_detection()
    test_non_circular_dependency()
    print("所有循环依赖检测测试通过!")
