# 贡献指南

欢迎参与 pytest-dynamic-params 的开发！本文档将帮助你了解如何参与贡献。

## 目录

- [开发环境设置](#开发环境设置)
- [运行测试](#运行测试)
- [代码风格](#代码风格)
- [提交规范](#提交规范)
- [贡献流程](#贡献流程)
- [发布流程](#发布流程)

## 开发环境设置

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/pytest-dynamic-params.git
cd pytest-dynamic-params
```

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. 安装开发依赖

```bash
# 以可编辑模式安装
pip install -e .[dev]

# 安装 pre-commit 钩子
pre-commit install
```

## 运行测试

### 基本测试

```bash
# 运行所有测试
pytest

# 运行测试并显示详细输出
pytest tests/ -v

# 运行特定测试文件
pytest tests/functional/test_basic_functionality.py -v
```

### 测试覆盖率

```bash
# 运行测试并生成覆盖率报告
pytest --cov=dynamic_params tests/

# 生成 HTML 覆盖率报告
pytest --cov=dynamic_params tests/ --cov-report=html:coverage-html

# 生成 XML 覆盖率报告
pytest --cov=dynamic_params tests/ --cov-report=xml:coverage.xml
```

### 并行测试

```bash
# 使用 pytest-xdist 运行并行测试
pytest tests/ -n auto

# 指定 worker 数量
pytest tests/ -n 4
```

## 代码风格

### 遵循 PEP 8

本项目遵循 PEP 8 代码风格规范。

### Pre-commit 钩子

项目使用 pre-commit 进行代码质量检查：

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
```

**离线环境配置**：

如果无法访问 GitHub，可以选择以下方案：

**方案 1：使用镜像源（推荐）**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://gitee.com/mirrors/black  # 使用 Gitee 镜像
    rev: 23.1.0
    hooks:
      - id: black
```

**方案 2：首次安装后缓存**

```bash
# 在联网环境下执行一次，工具会缓存到 ~/.cache/pre-commit
pre-commit install
pre-commit run --all-files

# 之后可以在离线环境下使用缓存的工具
```

**方案 3：本地配置**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: black
        name: black
        entry: black
        language: python
        types: [python]
      - id: isort
        name: isort
        entry: isort
        language: python
        types: [python]
```

### 运行代码检查

```bash
# 运行 pre-commit 检查
pre-commit run --all-files

# 运行 Black 格式化
black src/ tests/

# 运行 Isort 排序导入
isort src/ tests/

# 运行 Flake8 检查
flake8 src/ tests/

# 运行 Mypy 类型检查
mypy src/
```

## 提交规范

本项目使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范。

### 提交类型

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码风格修改（不影响代码运行）
- `refactor`: 代码重构
- `test`: 测试更新
- `chore`: 其他改动（构建、依赖等）

### 提交格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 提交示例

```bash
# 新功能
git commit -m "feat(generator): 添加懒加载支持"

# 修复 bug
git commit -m "fix(parametrize): 修复 DynRef 引用问题"

# 文档更新
git commit -m "docs(readme): 更新使用示例"

# 代码重构
git commit -m "refactor(engine): 优化依赖解析算法"
```

## 贡献流程

### 1. Fork 仓库

在 GitHub 上 Fork 本仓库到你的账户。

### 2. 创建分支

```bash
# 切换到主分支
git checkout main

# 拉取最新代码
git pull origin main

# 创建功能分支
git checkout -b feature/your-feature-name
```

### 3. 开发功能

```bash
# 编写代码
# ...

# 编写测试
# ...

# 运行测试确保通过
pytest tests/
```

### 4. 提交更改

```bash
# 添加文件
git add .

# 运行 pre-commit 检查
pre-commit run

# 提交代码
git commit -m "feat: 添加你的功能"
```

### 5. 推送代码

```bash
# 推送到你的 Fork
git push origin feature/your-feature-name
```

### 6. 提交 Pull Request

1. 在 GitHub 上访问你的 Fork
2. 点击 "Pull Request" 按钮
3. 填写 Pull Request 描述
4. 等待代码审查

### 7. 代码审查

- 维护者会审查你的代码
- 可能需要根据反馈进行修改
- 审查通过后合并到主分支

## 发布流程

### 版本号规范

遵循 [Semantic Versioning](https://semver.org/)：

- `MAJOR.MINOR.PATCH` (例如：1.2.3)
- `MAJOR`: 不兼容的 API 更改
- `MINOR`: 向后兼容的新功能
- `PATCH`: 向后兼容的问题修复

### 发布步骤

1. **更新版本号**

```python
# src/dynamic_params/__init__.py
__version__ = "1.2.3"
```

2. **更新 CHANGELOG.md**

```markdown
## [1.2.3] - 2026-03-31

### Added
- 新功能 1
- 新功能 2

### Fixed
- Bug 修复 1
- Bug 修复 2
```

3. **创建 Git 标签**

```bash
git tag -a v1.2.3 -m "Release version 1.2.3"
git push origin v1.2.3
```

4. **发布到 PyPI**

```bash
# 安装构建工具
pip install build twine

# 构建分发包
python -m build

# 上传到 PyPI
twine upload dist/*
```

## CI/CD 流程

本项目使用 GitHub Actions 进行持续集成：

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11"]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: pip install -e .[dev]
    
    - name: Run tests
      run: pytest tests/ --cov=dynamic_params
```

## 代码审查清单

在提交代码审查前，请确保：

- [ ] 代码遵循 PEP 8 规范
- [ ] 所有测试通过
- [ ] 测试覆盖率不低于 90%
- [ ] 代码有适当的注释和文档
- [ ] 提交信息符合 Conventional Commits 规范
- [ ] 更新文档（如有必要）
- [ ] 更新 CHANGELOG.md（如有必要）

## 联系与维护者

- **项目维护者**：Your Name <your.email@example.com>
- **GitHub Issues**：[提交 Issue](https://github.com/yourusername/pytest-dynamic-params/issues)
- **讨论区**：[GitHub Discussions](https://github.com/yourusername/pytest-dynamic-params/discussions)

## 许可证

本项目使用 MIT 许可证。贡献代码即表示你同意将代码以 MIT 许可证发布。

---

感谢你的贡献！🎉
