---
name: "quick-fix"
description: "Quickly fixes common code issues and errors. Invoke when encountering linting errors, type errors, or common Python coding issues."
---

# 快速修复技能

## 一键修复
```bash
black src/ tests/ && isort src/ tests/
```

## 完整修复流程
```bash
# 1. 格式化
black src/ tests/
isort src/ tests/

# 2. 检查剩余问题
flake8 src/ tests/

# 3. 类型检查
mypy src/项目/

# 4. 运行测试
pytest tests/
```

## 常见问题修复

### 导入问题 (F401)
```python
# 问题：未使用的导入
import os  # 未使用
# 修复：删除未使用的导入
```

### 代码风格问题
```python
# 问题：行过长
result = some_very_long_function_name(arg1, arg2)
# 修复：换行
result = some_very_long_function_name(
    arg1, arg2
)
```

### 变量问题 (F841)
```python
# 问题：变量未使用
result = calculate()
return "done"
# 修复：使用变量或删除
```

### 类型问题
```python
# 问题：缺少类型注解
def process(data):
    return data
# 修复：添加类型注解
def process(data: dict[str, Any]) -> dict[str, Any]:
    return data
```

### 函数问题
```python
# 问题：参数默认值可变
def add_item(item, items=[]):
# 修复：使用 None
def add_item(item, items=None):
    if items is None:
        items = []
```

## 注意事项
1. 修复前先备份重要文件
2. 一次修复一个问题类型
3. 修复后运行测试确保功能正常
4. 自动修复优先于手动修复