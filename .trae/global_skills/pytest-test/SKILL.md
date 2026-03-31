---
name: "pytest-test"
description: "Runs pytest tests with coverage and allure reports. Invoke when user asks to run tests, check test coverage, or generate test reports."
---

# Pytest 测试技能

## 核心功能
- 运行单元测试、集成测试、功能测试
- 生成测试覆盖率报告
- 生成 allure 测试报告

## 测试命令

### 基本测试
```bash
pytest
pytest tests/unit/
pytest tests/integration/
pytest tests/functional/
pytest -m "not slow"
```

### 覆盖率测试
```bash
pytest --cov=src/项目 --cov-report=term-missing
pytest --cov=src/项目 --cov-report=html
pytest --cov=src/项目 --cov-report=xml
```

### Allure 报告
```bash
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

### 详细输出
```bash
pytest -v
pytest -v -s
pytest --durations=10
```

### 并行测试
```bash
pytest -n auto
```

### 失败处理
```bash
pytest -x
pytest --pdb
pytest --lf
```

## 常用组合
```bash
pytest -v --cov=src/项目 --cov-report=term-missing --alluredir=reports/allure-results
pytest -v -m "not slow" --tb=short
```

## 注意事项
1. 运行测试前确保已安装所有依赖
2. 并行测试可能影响某些依赖状态的测试