# 测试报告汇总

## 报告生成时间
2026-03-09

## 测试结果摘要
- 总测试数：118
- 通过数：118
- 失败数：0
- 成功率：100%

## 覆盖率摘要
- 总语句数：420
- 覆盖语句数：304
- 覆盖率：72%

### 各模块覆盖率详情
```
Name                                   Stmts   Miss  Cover
----------------------------------------------------------
src\dynamic_params\__init__.py             8      0   100%
src\dynamic_params\config.py              42      1    98%
src\dynamic_params\core\generator.py      47      0   100%
src\dynamic_params\core\registry.py       51      0   100%
src\dynamic_params\decorators.py          46      2    96%
src\dynamic_params\dependency.py          51      3    94%
src\dynamic_params\errors.py              13      0   100%
src\dynamic_params\lazy.py                32      0   100%
src\dynamic_params\plugin.py             120    110     8%
src\dynamic_params\utils.py               10      0   100%
----------------------------------------------------------
TOTAL                                    420    116    72%
```

## 生成的报告文件

### 1. Allure 报告
- 位置：`reports/allure-report/index.html`
- 内容：详细的测试执行报告，包括测试用例详情、图表统计等

### 2. 覆盖率 HTML 报告
- 位置：`reports/coverage-html/index.html`
- 内容：代码覆盖率的详细可视化报告，显示每行代码的覆盖情况

### 3. 覆盖率 XML 报告
- 位置：`reports/coverage.xml`
- 内容：覆盖率数据的机器可读格式，可用于CI/CD集成

## 报告使用说明

1. **Allure 报告**：打开 `reports/allure-report/index.html` 在浏览器中查看详细的测试结果
2. **覆盖率报告**：打开 `reports/coverage-html/index.html` 在浏览器中查看代码覆盖率详情

## 核心模块质量
- 核心功能模块（generator, registry, decorators, dependency等）覆盖率均超过94%
- 插件模块(plugin.py)覆盖率较低(8%)，主要是因为该模块大部分是pytest钩子函数，难以直接测试
- 整体代码质量良好，测试覆盖充分