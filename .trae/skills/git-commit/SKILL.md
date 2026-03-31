---
name: "git-commit"
description: "Generates conventional commit messages and manages git operations. Invoke when user asks to commit changes, create commits, or needs help with git commit messages."
---

# Git 提交技能 - 项目配置

## 项目 Scope

| Scope | 说明 | 对应目录 |
|-------|------|---------|
| dependency | 依赖处理 | src/dynamic_params/engine/dependency/ |
| generator | 参数生成 | src/dynamic_params/engine/generator/ |
| parametrize | 参数化处理 | src/dynamic_params/engine/parametrize/ |
| plugin | pytest 插件 | src/dynamic_params/plugin/ |
| public | 公共 API | src/dynamic_params/public/ |
| utils | 工具函数 | src/dynamic_params/utils/ |
| config | 配置管理 | src/dynamic_params/config.py |
| docs | 文档 | docs/ |
| tests | 测试 | tests/ |

## 提交流程

```bash
git status
git diff
git add .
```

**必须等待用户确认后再执行提交和推送！**

## 技能协作
- **使用 `pre-commit` 技能**：提交前检查
- **使用 `follow-up-check` 技能**：检查后续动作