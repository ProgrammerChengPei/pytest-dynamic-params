# 代码风格规则

## 核心规范
- Python 代码必须遵循 PEP8 规范
- 代码需符合项目 .pre-commit-config.yaml 中定义的规范
- 默认使用 pytest 作为测试框架，使用 allure 生成测试报告，生成测试覆盖率报告

## 代码质量工具
- **Black**：代码格式化
- **Isort**：导入排序
- **Flake8**：代码风格检查
- **Mypy**：类型检查

## 检查流程
1. 提交前运行 pre-commit 检查
2. 运行完整测试套件
3. 检查测试覆盖率
4. 进行代码审查

## 参考技能
- 使用 `pre-commit` 技能执行代码质量检查
- 使用 `code-review` 技能进行详细代码审查
- 使用 `pytest-test` 技能运行测试和生成覆盖率报告
- 使用 `quick-fix` 技能修复常见代码问题