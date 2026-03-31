---
name: "dev-workflow"
description: "Manages development workflow including feature development, bug fixing, and release process."
---

# 项目开发工作流技能

## 开发流程

### 功能开发
```bash
git checkout -b feature/feature-name
# 编写代码...
pytest tests/
pre-commit run --all-files
```

### Bug 修复
```bash
git checkout -b fix/bug-name
# 编写失败测试重现 bug
# 修复 bug
```

### 版本发布
```bash
# 1. 更新版本号
# 2. 更新 CHANGELOG
pytest --cov=src/项目
pre-commit run --all-files
python -m build
twine upload dist/*
git tag -a v0.x.0 -m "Release v0.x.0"
```

## 代码规范
- 最低支持 Python 3.8
- 使用类型提示
- 遵循 PEP8 规范

## 导入顺序
1. 标准库
2. 第三方库
3. 本地模块

## 注意事项
1. 新功能必须有测试
2. 保持向后兼容性
3. 使用语义化版本