---
name: "code-review"
description: "Reviews code for PEP8 compliance, type hints, best practices and bugs. Invoke when user asks for code review, before committing changes, or after implementing new features."
---

# 代码审查技能 - 项目配置

## 审查流程

### 1. 代码质量基础检查
**使用 `pre-commit` 技能执行基础检查：**
- 运行 pre-commit 检查
- 使用 `quick-fix` 技能修复基础问题

### 2. 详细代码审查
在通过基础检查后，进行详细审查，关注架构、安全、性能等方面

### 3. 审查报告生成
使用标准模板记录审查结果和问题

## 技能协作
- **使用 `pre-commit` 技能**：执行基础代码质量检查
- **使用 `quick-fix` 技能**：修复常见的 linting 和类型问题
- **使用 `pytest-test` 技能**：验证代码修改后的功能正确性