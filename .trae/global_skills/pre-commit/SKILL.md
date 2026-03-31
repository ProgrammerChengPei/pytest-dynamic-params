---
name: "pre-commit"
description: "Manages pre-commit hooks for code quality checks. Invoke when running pre-commit, fixing linting issues, or setting up code quality tools."
---

# Pre-commit 技能

## 核心功能
- 执行 pre-commit 本地 hooks
- 运行 Black、Isort、Flake8、Mypy 检查

## 重要规则
**使用系统安装的工具，避免从网络拉取依赖！**

## 工具说明

### Black - 代码格式化
```bash
black --check src/ tests/
black src/ tests/
```

### Isort - 导入排序
```bash
isort --check-only src/ tests/
isort src/ tests/
```

### Flake8 - 代码风格检查
```bash
flake8 src/ tests/
```

### Mypy - 类型检查
```bash
mypy src/项目/
```

## 常用命令
```bash
pre-commit run --all-files
pre-commit run
pre-commit run black --all-files
```

## 注意事项
1. **使用系统安装的工具**
2. 提交前必须通过所有检查
3. 优先使用自动修复（black, isort）