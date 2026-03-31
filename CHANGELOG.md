# 更新日志

本文件记录项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，
项目遵循 [语义化版本](https://semver.org/spec/v2.0.0.html) 规范。

## v0.3.0 - 2026-03-31

### ⚠️ 重大变更

- **装饰器重命名**：
  - `@generator` → `@param_generator`
  - `@parametrize_test` 保持不变
  - `@parametrize_generator` 保持不变
  - 注意：此变更不保持向后兼容性！

### 🎯 新增功能

- **xdist 生成器同步机制**：
  - 实现基于文件的生成器数据同步
  - 支持 pytest-xdist 并行测试执行
  - 自动预加载 session/module 级别生成器
  - 支持外部资源（数据库、API）的生成器
  - Worker 独立连接池管理

### 🔨 重构与优化

- **项目架构重构**：
  - 完全重构为 engine 模块化架构
  - 新增 `engine/dependency/` 目录（依赖解析）
  - 新增 `engine/generator/` 目录（生成器核心）
  - 新增 `engine/parametrize/` 目录（参数化处理）
  - 新增 `plugin/compatibility/` 目录（插件兼容性）

- **装饰器系统优化**：
  - 统一装饰器命名规范
  - 分离装饰器定义与实现
  - 优化装饰器参数处理

- **依赖解析优化**：
  - 改进循环依赖检测
  - 优化依赖解析顺序

- **缓存机制改进**：
  - 优化缓存策略
  - 支持懒加载
  - 改进缓存失效处理

- **pytest 插件优化**：
  - 重构插件钩子实现
  - 新增兼容性处理模块
  - 优化参数化处理器

### 🧪 测试体系完善

- **新增测试目录**：
  - `tests/compatibility/` - pytest 插件兼容性测试
  - `tests/functional/` - 功能测试整合
  - `tests/integration/` - 集成测试整合
  - `tests/unit/` - 单元测试模块化
  - `tests/performance/` - 性能测试完善

- **新增测试类型**：
  - xdist 同步机制测试
  - 外部资源生成器测试
  - 依赖解析测试
  - 缓存和懒加载测试
  - 大规模参数化性能测试

- **删除过时测试**：
  - 删除 `tests/legacy/` 目录
  - 删除 `tests/fixtures/` 目录
  - 删除 `tests/generators/` 目录
  - 删除 `tests/utils/` 目录

### 📚 文档与工具

- **新增文档**：
  - `CONTRIBUTING.md` - 开发者贡献指南
  - `docs/comparison.md` - 与原生 pytest 对比
  - `specs/详细设计.md` - 详细设计文档
  - `specs/架构设计.md` - 架构设计文档

- **TalkTree 集成**：
  - 集成 TalkTree 对话管理系统 v0.2.0
  - 新增话题树、记忆管理和快照功能
  - 新增上下文导航和持久化技能

- **配置优化**：
  - 新增 `pytest.ini` 配置文件
  - 优化 `.pre-commit-config.yaml`
  - 更新 `.coveragerc` 配置

- **文档更新**：
  - 更新 `README.md` 示例代码和装饰器用法
  - 更新 `docs/usage-guide.md` 使用指南
  - 更新 `docs/STRUCTURE.md` 项目结构
  - 新增 `docs/comparison.md` 与原生 pytest 对比
  - 新增 `docs/xdist_sync_solution.md` xdist 同步方案
  - 新增 `docs/sync_integration.md` 同步机制集成
  - 新增 `docs/xdist_external_resource_solution.md` 外部资源方案

### 🔧 技术细节

- **新增模块**：
  - `src/dynamic_params/__version__.py` - 版本管理
  - `src/dynamic_params/config.py` - 配置管理
  - `src/dynamic_params/engine/generator/sync_manager.py` - 同步管理器
  - `src/dynamic_params/engine/generator/worker_pool.py` - Worker 连接池
  - `src/dynamic_params/engine/generator/xdist_sync.py` - xdist 同步
  - `src/dynamic_params/engine/parametrize/combinator.py` - 参数组合器
  - `src/dynamic_params/engine/parametrize/processor.py` - 参数化处理器
  - `src/dynamic_params/engine/dependency/graph.py` - 依赖图
  - `src/dynamic_params/engine/dependency/resolver.py` - 依赖解析器

- **删除模块**：
  - `src/dynamic_params/core/` - 旧核心模块
  - `src/dynamic_params/engine/config.py` - 旧配置模块
  - `src/dynamic_params/engine/dependency.py` - 旧依赖模块
  - `src/dynamic_params/plugin.py` - 旧插件模块
  - `src/dynamic_params/plugin/processors/` - 旧处理器模块

## v0.2.0 - 2026-03-12

### 主要变更

- 将 `with_dynamic_params` 装饰器重命名为 `dynamic_params`，注意此变更不保持向后兼容性！
- 更新了 pyproject.toml 中的作者信息
- 添加了项目主页和仓库链接到 pyproject.toml
- 添加了关键词以提高可发现性
- 更新了分类器，添加了更具体的 Python 版本
- 更新了 README.md 中的示例代码
- 增强了文档，添加了详细的问题解决方案和使用示例

## v0.1.0 - 2026-03-11

### 初始发布

- pytest-dynamic-params 插件的初始发布

### 核心功能

- **解决参数化时机冲突**：通过在测试运行阶段执行参数生成，支持在参数生成器中使用 fixture 的值
- **解决动态数据生成困难**：允许在参数生成器中调用依赖 fixture 的函数，实现动态数据生成
- **解决复杂的参数组合**：自动处理参数收集、组合和动态生成，无需手动编写钩子函数
- **解决依赖管理缺失**：自动分析和处理参数间的依赖关系，按正确顺序执行生成器

### 技术特性

- 动态参数生成功能
- 支持参数依赖和循环依赖检测
- 缓存机制以提高性能
- 延迟加载支持

### 测试与文档

- 全面的测试覆盖
- 详细的文档和使用示例

