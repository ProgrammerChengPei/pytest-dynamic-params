# pytest-dynamic-params 文件结构

本文档详细说明了 `pytest-dynamic-params` 插件的内部架构和模块设计。

## 项目目录结构

```
├── src/                  # 源代码
│   └── dynamic_params/   # 主要源代码
│       ├── engine/        # 内部引擎
│       │   ├── __init__.py      # 引擎导出
│       │   ├── config.py        # 配置管理
│       │   ├── dependency.py    # 依赖解析
│       │   └── registry.py      # 生成器注册表
│       ├── plugin/        # 插件实现
│       │   ├── __init__.py          # 插件导出
│       │   ├── pytest_plugin.py     # 核心插件逻辑
│       │   ├── processors/          # 装饰器处理器
│       │   │   ├── __init__.py      # 处理器导出
│       │   │   ├── use_generators.py # @use_generators 处理器
│       │   │   └── dynamic_parametrize.py # @dynamic_parametrize 处理器
│       │   └── utils.py             # 插件工具函数
│       ├── public/        # 公共 API
│       │   ├── __init__.py          # API 导出
│       │   ├── decorators/          # 装饰器
│       │   │   ├── __init__.py      # 装饰器导出
│       │   │   ├── generator.py     # @generator 装饰器
│       │   │   ├── use_generators.py # @use_generators 装饰器
│       │   │   └── dynamic_parametrize.py # @dynamic_parametrize 装饰器
│       │   └── generators/          # 生成器核心类
│       │       ├── __init__.py      # 生成器导出
│       │       ├── generator.py     # Generator 类
│       │       └── lazy.py          # 懒加载相关
│       ├── utils/         # 通用工具
│       │   ├── __init__.py          # 工具导出
│       │   └── helpers.py           # 辅助函数
│       ├── __init__.py           # 包入口点和公共接口
│       ├── errors.py             # 错误类定义
│       ├── py.typed              # 类型提示标记文件
│       └── types.py              # 类型定义
├── tests/                # 测试代码
│   ├── fixtures/         # 测试夹具
│   ├── functional/       # 功能测试
│   ├── generators/       # 测试生成器
│   ├── integration/      # 集成测试
│   ├── performance/      # 性能测试
│   ├── unit/             # 单元测试
│   ├── utils/            # 测试工具
│   └── conftest.py       # 测试配置文件
├── examples/             # 使用示例
├── docs/                 # 文档
├── specs/                # 项目规格说明
└── ...
```

## 核心模块详解

### 1. `src/dynamic_params/public/generators/generator.py` - 生成器核心实现
- `Generator`: 生成器核心类，负责执行参数生成逻辑、缓存和依赖管理
- 实现了参数生成的生命周期管理
- 支持多种作用域（function/class/module/session）
- 支持缓存和懒加载功能

### 2. `src/dynamic_params/engine/registry.py` - 生成器注册表
- `GeneratorRegistry`: 单例模式的生成器注册表，管理所有已注册的参数生成器
- 负责生成器的注册、查找和生命周期管理
- 提供按作用域管理的缓存机制

### 3. `src/dynamic_params/public/decorators/` - 装饰器系统
- `generator`: 参数生成器装饰器，用于标记参数生成函数
  - 支持作用域配置（scope参数）
  - 支持缓存配置（cache参数）
  - 支持懒加载配置（lazy参数）
- `use_generators`: 动态参数装饰器，用于关联测试函数和参数生成器
  - 验证参数映射的有效性
  - 确保生成器已被正确装饰
- `dynamic_parametrize`: 动态参数化装饰器，支持在参数化中使用DynRef引用

### 4. `src/dynamic_params/errors.py` - 异常体系
- `DynamicParamError`: 基础异常类
- `MissingParameterError`: 缺失参数异常，当依赖的参数在测试环境中不可用时抛出
- `InvalidGeneratorError`: 无效生成器异常，当函数未使用@generator装饰器标记时抛出
- `CircularDependencyError`: 循环依赖异常，当检测到参数生成器之间存在循环依赖时抛出
- `ExecutionError`: 执行异常，当生成器函数执行失败时抛出
- `ConfigurationError`: 配置异常，当配置无效时抛出

### 5. `src/dynamic_params/public/generators/lazy.py` - 懒加载机制
- `LazyResult`: 懒加载结果包装器，推迟参数生成直到实际需要
- `generate_lazy_combinations`: 生成懒加载参数组合的函数
- 提高性能，避免不必要的参数生成

### 6. `src/dynamic_params/plugin/pytest_plugin.py` - pytest插件实现
- `pytest_configure`: pytest配置钩子，注册插件标记
- `pytest_generate_tests`: 生成测试参数钩子，处理动态参数生成

### 7. `src/dynamic_params/engine/dependency.py` - 依赖解析引擎
- `resolve_dependency_order`: 解析生成器间的依赖关系并按拓扑排序
- 实现了基于Kahn算法的拓扑排序
- 检测循环依赖并提供详细的错误信息

### 8. `src/dynamic_params/engine/config.py` - 配置管理系统
- `DynamicParamConfig`: 动态参数配置类
- 管理缓存、作用域等配置选项
- 支持多种配置源（命令行、配置文件、环境变量）

### 9. `src/dynamic_params/utils/helpers.py` - 通用工具函数
- 提供参数处理、类型检查等通用功能
- 包含辅助函数以简化开发
- 提供函数签名提取、参数名验证等功能

### 10. `src/dynamic_params/types.py` - 类型定义
- 定义项目中使用的类型提示
- 提高代码的可读性和类型安全性

