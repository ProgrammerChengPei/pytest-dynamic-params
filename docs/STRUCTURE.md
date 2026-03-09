# pytest-dynamic-params 源码架构详解

本文档详细说明了 `pytest-dynamic-params` 插件的内部架构和模块设计。

## 项目目录结构

```
├── src/                  # 源代码
│   └── dynamic_params/   # 主要源代码
│       ├── core/         # 核心组件
│       │   ├── generator.py      # 参数生成器类
│       │   └── registry.py       # 生成器注册表
│       ├── __init__.py           # 包入口点和公共接口
│       ├── config.py             # 配置管理模块
│       ├── decorators.py         # 装饰器定义
│       ├── dependency.py         # 依赖解析模块（含循环依赖检测）
│       ├── errors.py             # 错误类定义
│       ├── lazy.py               # 懒加载相关实现
│       ├── plugin.py             # pytest插件实现
│       └── utils.py              # 工具函数
├── tests/                # 测试代码
├── examples/             # 使用示例
├── docs/                 # 文档
├── specs/                # 项目规格说明
├── reports/              # 测试报告
└── ...
```

## 核心模块详解

### 1. `src/dynamic_params/core/generator.py` - 参数生成器实现
- `ParamGenerator`: 参数生成器核心类，负责执行参数生成逻辑、缓存和依赖管理
- 实现了参数生成的生命周期管理
- 支持多种作用域（function/class/module/session）

### 2. `src/dynamic_params/core/registry.py` - 生成器注册表
- `GeneratorRegistry`: 单例模式的生成器注册表，管理所有已注册的参数生成器
- 负责生成器的注册、查找和生命周期管理
- 提供线程安全的访问机制

### 3. `src/dynamic_params/decorators.py` - 装饰器系统
- `param_generator`: 参数生成器装饰器，用于标记参数生成函数
  - 支持作用域配置（scope参数）
  - 支持缓存配置（cache参数）
  - 支持懒加载配置（lazy参数）
- `with_dynamic_params`: 动态参数装饰器，用于关联测试函数和参数生成器
  - 验证参数映射的有效性
  - 确保生成器已被正确装饰

### 4. `src/dynamic_params/errors.py` - 异常体系
- `DynamicParamError`: 基础异常类
- `MissingParameterError`: 缺失参数异常，当依赖的参数在测试环境中不可用时抛出
- `InvalidGeneratorError`: 无效生成器异常，当函数未使用@param_generator装饰器标记时抛出
- `CircularDependencyError`: 循环依赖异常，当检测到参数生成器之间存在循环依赖时抛出

### 5. `src/dynamic_params/lazy.py` - 懒加载机制
- `LazyResult`: 懒加载结果包装器，推迟参数生成直到实际需要
- `generate_lazy_combinations`: 生成懒加载参数组合的函数
- 提高性能，避免不必要的参数生成

### 6. `src/dynamic_params/plugin.py` - pytest插件实现
- `pytest_configure`: pytest配置钩子，注册插件标记
- `pytest_generate_tests`: 生成测试参数钩子，处理动态参数生成
- `pytest_runtest_setup`: 测试运行前设置钩子
- `pytest_runtest_call`: 测试调用钩子，注入动态参数

### 7. `src/dynamic_params/dependency.py` - 依赖解析引擎
- `resolve_dependency_order`: 解析生成器间的依赖关系并按拓扑排序
- `detect_circular_dependency`: 检测循环依赖并提供详细的错误信息
- 实现了基于图论的依赖解析算法

### 8. `src/dynamic_params/config.py` - 配置管理系统
- `DynamicParamConfig`: 动态参数配置类
- 管理缓存、作用域等配置选项
- 支持多种配置源（命令行、配置文件、环境变量）

### 9. `src/dynamic_params/utils.py` - 通用工具函数
- 提供参数处理、类型检查等通用功能
- 包含辅助函数以简化开发

## 架构设计原则

1. **单一职责原则**: 每个模块都有明确的功能定位，职责分离清晰
2. **开闭原则**: 系统对扩展开放，对修改关闭，支持新的参数生成器类型
3. **依赖倒置**: 高层模块不依赖低层模块，都依赖于抽象接口
4. **接口隔离**: 提供细粒度的接口，避免胖接口问题
5. **可测试性**: 模块设计考虑了单元测试的需求，各组件松耦合