# pytest-dynamic-params 组合集成测试

## 测试策略

本测试目录验证 pytest-dynamic-params 插件内部各特性的组合使用情况，确保各个装饰器和功能能够正确协同工作。

作用域和缓存，是单个插件内部特性，和其他插件、pytest 无关，不用做集成测试。

## 组件

**pytest 原生组件** ：

- fixture
- pytest.mark.parametrize

**插件组件**：

- param_generator
- parametrize_test
- parametrize_generator
- parametrize_fixture
- DynRef

每个组件使用下面的缩写：

| 完整名称 | 缩写 |
|---------|------|
| `fixture` | `fix` |
| `pytest.mark.parametrize` | `mark_param` |
| `param_generator` | `gen` |
| `parametrize_test` | `param_test` |
| `parametrize_generator` | `param_gen` |
| `parametrize_fixture` | `param_fix` |
| `DynRef` | `dynref` |

## 组合生成规则

1. 先测试单个插件组件。pytest 原生组件不计入插件个数，可以在任意位置使用。
2. 执行已有测试用例，根据测试结果，确定哪些组合是支持的。
3. 等待用户确认测试结果，判断是否和开发意图一致、决定是否需要修改源码。
4. 如果某个组合没有任何成功的测试用例，说明该组合不支持，无需在此基础上添加更多的插件组件进一步组合。从支持的组合中选择一个作为基础，在此基础上逐个添加其他插件组件，生成测试用例。
5. 重复步骤2到4，直到所有支持的组合都被测试过。

## 命名规则

- 目录：
    `test_combo_{插件组件个数}/`，pytest 原生组件不算在内，例如 `test_combo_2/` 表示两个插件组件的组合。
- 文件：
    `test_{插件组件 1的缩写}_and_{插件组件 2的缩写}_and_{插件组件 3的缩写}.py`，所有组件名称使用 `and` 连接。
- 测试用例：

    测试文件名已经包含了组合信息，不需要在测试用例名中重复体现，测试用例名直接体现被测功能即可。

    例如：不使用 `test_gen_and_param_test_conditional_expression`，而是使用 `test_conditional_expression`。

## 测试用例状态标记

每个用例都必须使用 `@pytest.mark.{status}` 来标识测试用例的期望状态。

status 取值及含义：

| 状态 | 含义 | 使用场景 |
|------|------|---------|
| `passed` | 测试通过 | 正常工作的测试用例 |
| `failed` | 测试失败 | 运行时断言失败的测试用例 |
| `error` | 测试出错 | 运行时抛出异常的测试用例 |
| `skipped` | 测试跳过 | 被跳过的测试用例 |

## 测试用例生成

### 测试用例分类

- 失败示例：
  - 展示常见的错误使用方式以及错误原因
  - 会导致收集失败的用例示例，或可以收集但是执行后状态为 `failed` 或 `error`的用例
  - 必须只使用组合中的插件组件，不能随意增加或减少插件组件，但是 pytest 原生组件可以随意使用
  - 如果会导致收集失败，标记为 `pytest.mark.skip_collection_error(reason={导致收集失败的原因})` 跳过收集。注意不是使用 `@pytest.mark.skip` 去跳过, `@pytest.mark.skip` 只在执行阶段生效。
  - 如果可以收集，标记为 `pytest.mark.{status}`

- 推荐用法示例：
  - 每个失败示例都必须给出一个能解决失败问题的推荐用法示例，展示插件实现相同功能的推荐使用方式
  - 状态为 `passed`
  - 标记为 `@pytest.mark.recommended`
  - 可以使用解决问题必要的任意组件，包含不在组合内的插件组件和 pytest 原生组件
  - 如果支持并且推荐使用，既要展示只使用 pytest 原生组件的测试用例，又要展示使用插件的测试用例，这样才能直观地说明插件的独特优势

- 成功示例：
  - 展示插件比原生pytest多出的、或更好用的功能及其正确使用方式
  - status 为 `passed`
  - 必须只使用组合中的插件组件，不能随意增加或减少插件组件，但是 pytest 原生组件可以随意使用
  - 应尽可能覆盖更多的插件使用场景

### 测试用例格式

测试文件头、测试用例的格式如下。

**测试文件头格式**：

```python
"""
组件 1 + 组件 2 组合测试

测试 {组件 1} 与 {组件 2} 的组合使用
探索正确的使用方式，探索不支持的使用方式并给出替代方案。

结论：{简要说明使用要点}
"""
```

**失败示例格式**：

- 在前面注释 `# 失败示例 {失败序号}：{测试内容}`
- 在用例前面标记 `@pytest.mark.skip_collection_error` 或 `@pytest.mark.{status}`

```python
# 失败示例 01: @pytest.mark.parametrize 不能参数化 fixture
@pytest.fixture
def _double(value):
    """基础 fixture"""
    return value * 2

@pytest.mark.skip_collection_error(reason="AI 自己补充")
@pytest.mark.parametrize("value", [1, 2, 3])
def test_mark_param_fix(_double):
    """测试基础参数生成"""
    assert fix_a in [2, 4, 6]
```

**推荐用法示例格式**：

- 在前面注释 `# {失败示例的用例名} 的推荐用法示例 {推荐序号}：{推荐内容}`
- 每个失败示例的推荐用法示例的序号，都从1开始
- 用例名 `{失败示例的用例名}_recommended`
- 在用例前面标记 `@pytest.mark.recommended`

```python
# test_mark_param_and_fix 的推荐用法示例 01: @param_generator 可以被参数化后，再通过 @parametrize_test 参数化测试用例
@pytest.mark.recommended
@param_generator
def gen_double(value):
    """基础参数生成器"""
    return value * 2

@pytest.mark.parametrize("value", [1, 2, 3])
@parametrize_test("double_", gen_double)
def test_mark_param_and_fix_recommended(value, double_):
    """测试基础参数生成"""
    assert double == 2 * value
    
```

**成功示例格式**：

- 在前面注释 `# 成功示例 {成功序号}：{测试内容}`
- 在用例前面标记 `@pytest.mark.passed`

```python
# 成功示例 01: parametrize_test 基础参数化
def generate_test_cases():
    cases = []
    for i in range(1, 6):
        cases.append((i, i * 2))
    return cases

@pytest.mark.passed
@parametrize_test("num, doubled", generate_test_cases())
def test_param_test(num, doubled):
    assert num * 2 == doubled
```

### 测试用例生成规则

每种组件组合，采用"(失败示例 -> 推荐用法示例) + 成功示例"模式，必须包含失败示例和成功示例中的其中一个，可以都包含但不是必须。

## 运行测试

```bash
# 运行所有组合测试
pytest -v

# 运行特定标记
pytest test_combo_02/ -v -m passed
pytest test_combo_02/ -v -m recommended

# 运行特定组合个数
pytest test_combo_02/

# 运行特定文件
pytest test_combo_02/test_gen_and_param_test.py

```

## 注意事项

1. 所有测试文件都应该导入必要的组件
2. 使用统一的命名和代码风格
3. 测试应该独立运行，不依赖其他测试的执行顺序
4. 测试应该覆盖所有可能的场景，包括边界条件和异常情况

## 依赖的 pytest 插件

- `pytest-skip-collection-error`: 用于标记并跳过收集错误的测试用例
