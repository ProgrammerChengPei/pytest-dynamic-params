# pytest-dynamic-params 项目结构说明

本文档说明项目的文件组织和目录结构，帮助开发者和用户快速定位文件。

## 📁 项目目录总览

```
pytest-dynamic-params/
├── src/dynamic_params/          # 源代码
├── tests/                       # 测试代码
├── docs/                        # 文档
├── specs/                       # 规格说明
├── examples/                    # 使用示例
├── README.md                    # 快速入门
├── CONTRIBUTING.md              # 贡献指南
└── ...
```

## 📂 详细目录结构

### 源代码目录 (`src/dynamic_params/`)

```
src/dynamic_params/
├── __init__.py                  # 包入口，导出公共 API
├── types.py                     # 类型定义
├── errors.py                    # 异常类定义
├── py.typed                     # PEP 561 类型提示标记
│
├── public/                      # 公共 API（用户直接使用）
│   ├── __init__.py
│   ├── decorators/              # 装饰器
│   │   ├── param_generator.py         # @param_generator
│   │   └── parametrize_fixture.py     # @parametrize_fixture
│   ├── generators/              # 生成器核心类
│   │   ├── base.py                    # GeneratorBase 类
│   │   ├── sync_manager.py            # SyncManager 同步管理器
│   │   └── worker_pool.py             # WorkerPool 连接池

│
├── engine/                      # 内部引擎（不直接暴露给用户）
│   ├── __init__.py
│   ├── config.py                # 配置管理
│   ├── dependency.py            # 依赖解析
│   └── registry.py              # 生成器注册表
│
└── plugin/                      # pytest 插件实现
    ├── __init__.py
    ├── pytest_plugin.py         # 核心插件逻辑
    └── utils.py                 # 插件工具函数
```

### 测试目录 (`tests/`)

```
tests/
├── conftest.py                  # pytest 配置和共享 fixture
├── unit/                        # 单元测试
│   ├── test_decorators.py       # 测试装饰器
│   └── test_generators.py       # 测试生成器
│
├── functional/                  # 功能测试
│   ├── test_basic_functionality.py  # 基础功能
│   ├── test_fixture_integration.py  # fixture 集成
│   └── test_parametrize.py      # 参数化测试
│
├── integration/                 # 集成测试
│   ├── test_generator_integration.py  # 生成器集成
│   └── test_cache_lazy_integration.py # 缓存和懒加载集成
│
├── performance/                 # 性能测试
│   ├── test_caching_performance.py    # 缓存性能
│   └── test_lazy_loading_performance.py # 懒加载性能
│
└── sync_tests/                  # 同步机制测试
    └── test_sync_integration.py # 并行测试同步集成测试
```

### 文档目录 (`docs/`)

```
docs/
├── usage-guide.md               # 用户使用指南（详细教程）
├── STRUCTURE.md                 # 本文件（项目结构说明）
├── comparison.md                # 与 pytest.mark.parametrize 对比
└── reports-*.md                 # 历史测试报告
```

### 规格目录 (`specs/`)

```
specs/
├── 需求.md                      # 需求规格文档
├── 架构设计.md                  # 架构设计（技术决策、组件职责）
├── 详细设计.md                  # 详细设计（实现细节、算法）
└── 待办.md                      # 待办事项
```

## 📄 根目录文件说明

| 文件 | 用途 | 目标读者 |
|------|------|---------|
| `README.md` | 快速入门指南 | 新用户 |
| `CONTRIBUTING.md` | 贡献指南 | 贡献者 |

## 🔍 快速定位

### 查找装饰器实现

```
@param_generator       → src/dynamic_params/public/decorators/param_generator.py
@parametrize_fixture   → src/dynamic_params/public/decorators/parametrize_fixture.py
```

### 查找核心类

```
GeneratorBase    → src/dynamic_params/public/generators/base.py
SyncManager      → src/dynamic_params/public/generators/sync_manager.py
WorkerPool       → src/dynamic_params/public/generators/worker_pool.py
```

### 查找引擎组件

```
配置管理    → src/dynamic_params/engine/config.py
依赖解析    → src/dynamic_params/engine/dependency.py
注册表      → src/dynamic_params/engine/registry.py
```

### 查找测试

```
单元测试      → tests/unit/
功能测试      → tests/functional/
集成测试      → tests/integration/
性能测试      → tests/performance/
同步测试      → tests/sync_tests/
```

## 📚 文档导航

### 用户文档

- **快速入门** → [README.md](../README.md)
- **详细使用指南** → [docs/usage-guide.md](usage-guide.md)
- **功能对比** → [docs/comparison.md](comparison.md)

### 开发文档

- **贡献指南** → [CONTRIBUTING.md](../CONTRIBUTING.md)
- **项目结构** → 本文件
- **需求** → [specs/需求.md](../specs/需求.md)
- **架构设计** → [specs/架构设计.md](../specs/架构设计.md)
- **详细设计** → [specs/详细设计.md](../specs/详细设计.md)

## 🏗️ 架构 vs 结构

**本文档与架构设计文档的区别**：

- **STRUCTURE.md（本文档）**：说明**文件在哪里**，帮助快速定位
- **specs/架构设计.md**：说明**为什么这样设计**，包含技术决策、组件职责、数据流等

**推荐阅读顺序**：

1. 新用户：README.md → usage-guide.md
2. 贡献者：CONTRIBUTING.md → STRUCTURE.md → 架构设计.md
3. 深度开发：架构设计.md → 详细设计.md → 源代码

---

**最后更新**: 2026-03-31
