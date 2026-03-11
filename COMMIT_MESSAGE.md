feat: 完成 pytest-dynamic-params 插件的开发与配置优化

**主要变更**：

1. **项目结构完善**：
   - 创建了完整的项目目录结构，包括 src、tests、docs、examples 等目录
   - 添加了 LICENSE、README.md 等基础文件
   - 配置了 pyproject.toml 和 setup.py 构建文件

2. **核心功能实现**：
   - 实现了动态参数生成器核心功能
   - 支持参数依赖管理和循环依赖检测
   - 实现了缓存机制，提升性能
   - 支持延迟加载和不同作用域的参数管理

3. **测试覆盖**：
   - 编写了全面的单元测试和功能测试
   - 实现了性能测试和基准测试
   - 测试覆盖了各种边缘情况和错误处理

4. **代码质量优化**：
   - 配置了 pre-commit 钩子，确保代码质量
   - 统一了导入方式，从 `src.dynamic_params` 改为 `dynamic_params`
   - 优化了 mypy 配置，解决了模块重复识别问题
   - 修复了 flake8 代码风格错误
   - 为动态添加的属性添加了类型注解忽略注释

5. **配置管理**：
   - 将 mypy 配置迁移到 pyproject.toml
   - 配置了 flake8 忽略类型注解检查
   - 优化了 black 和 isort 配置

**技术亮点**：
- 支持复杂的参数依赖关系
- 高效的缓存机制减少重复计算
- 良好的错误处理和用户友好的错误信息
- 与 pytest 原生功能的无缝集成
- 支持 xdist 并行测试

**使用方式**：
```python
from dynamic_params import dynamic_param, with_dynamic_params

@dynamic_param
def param1():
    return [1, 2, 3]

@dynamic_param
def param2(param1):
    return [x * 2 for x in param1]

@with_dynamic_params
def test_example(param1, param2):
    assert param2 == param1 * 2
```

该插件为 pytest 提供了强大的动态参数生成能力，支持复杂的参数依赖关系，适用于需要动态生成测试参数的场景。