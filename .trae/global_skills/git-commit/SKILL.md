---
name: "git-commit"
description: "Generates conventional commit messages and manages git operations. Invoke when user asks to commit changes, create commits, or needs help with git commit messages."
---

# Git 提交技能

## 重要规则
**提交前必须等待用户确认！**

## Conventional Commits 格式
```
<type>(<scope>): <description>
[optional body]
[optional footer(s)]
```

## 提交类型

| 类型 | 说明 | 示例 |
|------|------|------|
| feat | 新功能 | feat: add new feature |
| fix | 修复 bug | fix: resolve bug |
| docs | 文档更新 | docs: update README |
| style | 代码格式 | style: format code |
| refactor | 重构代码 | refactor: extract module |
| perf | 性能优化 | perf: optimize |
| test | 测试相关 | test: add tests |
| chore | 构建/工具 | chore: update hooks |
| ci | CI 配置 | ci: add workflow |
| revert | 回滚提交 | revert: revert previous |

## 提交流程
```bash
git status
git diff
git add .
git commit -m "type(scope): description"
```

## 破坏性变更
```
feat(api)!: rename old to new
BREAKING CHANGE: API has been renamed.
```

## 注意事项
1. **必须等待用户确认**才能执行提交
2. 一个提交只做一件事
3. 不要提交敏感信息