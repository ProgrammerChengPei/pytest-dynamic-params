# 测试报告

此目录包含 pytest-dynamic-params 插件的测试报告。

## 报告类型

- Allure 报告：详细的测试执行报告
- 覆盖率报告：代码覆盖率分析

## 生成的报告

### Allure 报告
- 位置：`allure-report/index.html`
- 包含详细的测试执行结果、图表和统计信息

### 覆盖率报告
- HTML：`coverage-html/index.html`
- XML：`coverage.xml`
- 提供代码覆盖率指标和可视化

### 摘要
- 摘要：`docs\reports-summary.md`
- 包含测试结果和覆盖率指标的概述

## 报告生成

要重新生成报告，请运行：
```bash
python -m pytest tests/ --alluredir=reports/allure-results -clean --cov=src.dynamic_params --cov-report=html:reports/coverage-html --cov-report=xml:reports/coverage.xml --cov-report=term
allure serve reports/allure-results
```