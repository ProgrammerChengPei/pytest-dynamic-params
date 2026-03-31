---
name: "dev-workflow"
description: "Manages development workflow including feature development, bug fixing, and release process."
---

# 项目开发工作流技能 - 项目配置

## 项目结构
```
src/dynamic_params/
├── engine/           # 核心引擎
├── plugin/          # pytest 插件
├── public/          # 公共 API
└── utils/           # 工具函数

tests/
├── unit/            # 单元测试
├── integration/     # 集成测试
├── functional/      # 功能测试
└── performance/     # 性能测试
```

## 技能协作
- **使用 `git-commit` 技能**：生成规范的提交信息
- **使用 `pre-commit` 技能**：运行提交前检查
- **使用 `pytest-test` 技能**：运行测试验证
- **使用 `follow-up-check` 技能**：检查后续动作
- **使用 `update-docs` 技能**：更新项目文档