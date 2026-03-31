---
name: "code-review"
description: "Reviews code for PEP8 compliance, type hints, best practices and bugs. Invoke when user asks for code review, before committing changes, or after implementing new features."
---

# 代码审查技能

用于审查代码质量，确保符合 PEP8 规范、类型提示完整、遵循最佳实践。

## 审查清单

### 代码风格
- [ ] 符合 PEP8 规范
- [ ] 使用 4 空格缩进
- [ ] 行长度不超过 88 字符（Black 默认）
- [ ] 使用 UTF-8 编码
- [ ] 文件末尾有空行

### 命名规范
- [ ] 变量名使用 snake_case
- [ ] 类名使用 PascalCase
- [ ] 常量使用 UPPER_SNAKE_CASE
- [ ] 私有属性以单下划线开头
- [ ] 名称具有描述性，避免单字母

### 类型提示
- [ ] 函数参数有类型注解
- [ ] 函数返回值有类型注解
- [ ] 使用 typing 模块的类型
- [ ] 复杂类型使用 TypeAlias

### 文档字符串
- [ ] 公共函数有 docstring
- [ ] 公共类有 docstring
- [ ] 使用 Google 或 NumPy 风格
- [ ] 包含参数和返回值说明

### 错误处理
- [ ] 使用具体的异常类型
- [ ] 提供有意义的错误消息
- [ ] 适当使用 try-except
- [ ] 资源使用 with 语句管理

### 代码结构
- [ ] 函数单一职责
- [ ] 函数长度适中（建议 < 50 行）
- [ ] 避免深层嵌套
- [ ] 使用早返回减少嵌套

### 安全性
- [ ] 不硬编码敏感信息
- [ ] 不使用不安全的函数
- [ ] 输入验证

## 注意事项
1. 审查前确保代码可运行
2. 优先修复高优先级问题
3. 保持代码风格一致性
4. 新代码必须有对应测试