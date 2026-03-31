# 性能测试执行指南

## 📋 快速开始

### 前置要求

```bash
# 安装依赖
pip install pytest pytest-benchmark psutil

# 验证安装
pytest --version
pytest --benchmark-version
```

### 执行测试

```bash
# 方式 1：运行所有性能测试（推荐）
pytest tests/performance/ -v

# 方式 2：运行特定测试模块
pytest tests/performance/test_benchmarks.py -v
pytest tests/performance/test_caching_performance.py -v
pytest tests/performance/test_dependency_resolution.py -v
pytest tests/performance/test_large_scale_parametrization.py -v

# 方式 3：运行单个测试
pytest tests/performance/test_benchmarks.py::TestGeneratorBenchmarks::test_generator_creation_time -v

# 方式 4：生成性能报告
python tests/performance/test_runner.py
```

## 📊 测试模块说明

### 1. test_benchmarks.py - 基准测试（12 个测试）

**测试内容**：
- ✅ 生成器创建时间
- ✅ 生成器执行时间  
- ✅ 参数化开销
- ✅ DynRef 创建和表达式构建
- ✅ 装饰器应用时间
- ✅ 端到端参数化性能

**执行时间**：~0.3 秒

**关键指标**：
```
Generator creation time: < 10ms
Simple generator execution: < 50ms
Parametrization overhead: < 5ms
DynRef creation: < 1ms
```

### 2. test_caching_performance.py - 缓存性能测试（12 个测试）

**测试内容**：
- ✅ 缓存命中/未命中性能
- ✅ 不同作用域缓存（function、module、session）
- ✅ 缓存清除性能
- ✅ 缓存内存使用
- ✅ 缓存 vs 无缓存对比
- ✅ 并发缓存访问

**执行时间**：~0.9 秒

**关键指标**：
```
Cache hit: < 1ms
Cache miss: < 10ms
Session scope cache: < 3ms
```

### 3. test_dependency_resolution.py - 依赖解析测试（16 个测试）

**测试内容**：
- ✅ 依赖图构建（小型、大型、复杂）
- ✅ 循环依赖检测
- ✅ 拓扑排序性能
- ✅ DynRef 解析
- ✅ 依赖链解析
- ✅ 压力测试

**执行时间**：~0.4 秒

**关键指标**：
```
Small graph construction: < 10ms
Large graph construction: < 500ms
Cycle detection: < 200ms
Topological sort: < 500ms
```

### 4. test_lazy_loading_performance.py - 懒加载测试

**测试内容**：
- ⚠️ 懒加载初始化
- ⚠️ 懒加载与缓存结合
- ⚠️ 延迟执行优势
- ⚠️ 懒加载内存效率
- ⚠️ 常见懒加载模式
- ⚠️ 压力测试

**执行时间**：可变

**注意**：部分测试需要调整阈值以适配实际实现

### 5. test_large_scale_parametrization.py - 大规模参数化（17 个测试）

**测试内容**：
- ✅ 大型参数集（100、1000、10000+ 参数）
- ✅ 组合参数化
- ✅ 生成器扩展性
- ✅ 内存使用测试
- ✅ 压力测试
- ✅ 边界情况测试

**执行时间**：~0.5 秒

**关键指标**：
```
100 parameters: < 5ms avg
1000 parameters: < 5ms avg
Large parameter values: < 10ms avg
```

### 6. test_memory_efficiency.py - 内存效率测试

**测试内容**：
- ⚠️ 内存消耗测试
- ⚠️ 内存泄漏检测
- ⚠️ 垃圾回收行为
- ⚠️ 内存效率优化
- ⚠️ 常见内存使用模式
- ⚠️ 压力测试

**注意**：内存阈值因平台而异，需要根据实际环境调整

### 7. test_concurrency.py - 并发性能测试

**测试内容**：
- ⚠️ 线程安全性
- ⚠️ 并行执行
- ⚠️ pytest-xdist 兼容性模拟
- ⚠️ 分布式缓存
- ⚠️ 可扩展性测试
- ⚠️ 压力测试

**注意**：并发测试受环境影响较大，建议多次运行取平均值

## 🎯 性能阈值标准

### 核心操作阈值（必须满足）

| 测试项 | 阈值 | 严重级别 |
|--------|------|---------|
| 缓存命中 | < 1ms | 🔴 关键 |
| 缓存未命中 | < 10ms | 🔴 关键 |
| 依赖解析 | < 10ms | 🔴 关键 |
| 小型参数生成 | < 50ms | 🔴 关键 |
| 中型参数生成 | < 200ms | 🟡 警告 |
| 大型参数生成 | < 1000ms | 🟡 警告 |

### 内存阈值（参考）

| 测试项 | 阈值 | 说明 |
|--------|------|------|
| 基本生成器 | < 10MB | 正常范围 |
| 缓存生成器 | < 20MB | 正常范围 |
| 大型对象 | < 50MB | 可接受 |
| 压力测试 | < 200MB | 上限 |

## 📈 测试结果解读

### 通过标准

```
✅ 通过：测试执行时间 < 阈值 且 功能正确
⚠️ 警告：测试执行时间接近阈值（> 80% 阈值）
❌ 失败：测试执行时间 > 阈值 或 功能错误
```

### 示例输出

```
tests/performance/test_benchmarks.py::TestGeneratorBenchmarks::test_generator_creation_time PASSED [  8%]
tests/performance/test_benchmarks.py::TestGeneratorBenchmarks::test_simple_generator_execution PASSED [ 16%]

============================= 12 passed in 0.28s =============================
```

### 失败处理

如果测试失败：

1. **检查环境**：
   ```bash
   # 检查系统负载
   tasklist  # Windows
   top       # Linux/Mac
   
   # 检查内存使用
   taskmgr   # Windows
   free -h   # Linux
   ```

2. **重复测试**：
   ```bash
   # 运行 3 次取平均值
   pytest tests/performance/test_benchmarks.py -v --count=3
   ```

3. **查看详细错误**：
   ```bash
   pytest tests/performance/test_benchmarks.py -v --tb=long
   ```

4. **跳过已知问题**：
   ```bash
   # 跳过特定测试
   pytest tests/performance/ -v -k "not test_lazy_vs_eager_initialization"
   ```

## 🔧 测试配置

### 调整性能阈值

编辑 `tests/performance/conftest.py`：

```python
@pytest.fixture(scope="session")
def performance_thresholds():
    return {
        "cache_hit": 1,        # 单位：毫秒
        "cache_miss": 10,
        "lazy_load": 5,
        "dependency_resolve": 10,
        "param_generation_small": 50,
        "param_generation_medium": 200,
        "param_generation_large": 1000,
        "memory_usage_mb": 100,
    }
```

### 调整基准配置

```python
@pytest.fixture(scope="session")
def benchmark_config():
    return {
        "warmup_iterations": 3,      # 预热次数
        "benchmark_iterations": 10,  # 基准测试次数
        "sample_size": 100,          # 样本大小
        "large_sample_size": 10000,  # 大样本大小
        "stress_sample_size": 100000,# 压力测试样本大小
    }
```

## 📝 生成报告

### JSON 报告

```bash
python tests/performance/test_runner.py
```

生成 `performance_report.json`：

```json
{
  "metadata": {
    "start_time": "2026-03-30T10:00:00",
    "end_time": "2026-03-30T10:05:00",
    "total_tests": 98,
    "passed": 95,
    "failed": 3
  },
  "summary": {
    "avg_duration_ms": 15.2,
    "min_duration_ms": 0.5,
    "max_duration_ms": 450.0,
    "pass_rate": 0.97
  }
}
```

### Markdown 报告

生成 `performance_report.md`，包含：
- 测试摘要
- 按类别分组的结果
- 性能亮点（最快、最慢、平均）
- 详细测试列表

## 🚀 CI/CD 集成

### GitHub Actions 示例

```yaml
name: Performance Tests

on: [push, pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-benchmark psutil
      
      - name: Run performance tests
        run: |
          pytest tests/performance/ -v \
            --tb=short \
            --durations=10 \
            --json-report=performance_results.json
      
      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: performance-report
          path: |
            performance_results.json
            tests/performance/performance_report.md
      
      - name: Check performance thresholds
        run: |
          python scripts/check_thresholds.py performance_results.json
```

### Jenkins 示例

```groovy
pipeline {
    agent any
    
    stages {
        stage('Performance Tests') {
            steps {
                sh 'pip install -e .'
                sh 'pip install pytest pytest-benchmark psutil'
                sh 'pytest tests/performance/ -v --html=performance_report.html'
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAllHistory: true,
                        reportDir: '.',
                        reportFiles: 'performance_report.html',
                        reportName: 'Performance Report'
                    ])
                }
            }
        }
    }
}
```

## ⚠️ 已知问题和注意事项

### 1. 懒加载测试

**问题**：部分懒加载测试逻辑需要适配实际实现

**解决方案**：
```bash
# 暂时跳过有问题的测试
pytest tests/performance/test_lazy_loading_performance.py -v \
  -k "not test_lazy_vs_eager_initialization"
```

### 2. 内存测试

**问题**：内存阈值因平台而异

**解决方案**：
```python
# 在 conftest.py 中根据平台调整阈值
import sys

@pytest.fixture(scope="session")
def memory_threshold():
    if sys.platform == "win32":
        return 150  # Windows 阈值较高
    elif sys.platform == "darwin":
        return 120  # macOS
    else:
        return 100  # Linux
```

### 3. 并发测试

**问题**：并发测试受环境影响较大

**解决方案**：
```bash
# 多次运行取平均值
for i in {1..5}; do
  pytest tests/performance/test_concurrency.py --tb=no -q
done | awk '{sum+=$NF} END {print "Average:", sum/NR}'
```

## 📚 故障排除

### 常见问题

#### Q1: 测试随机失败

**原因**：系统负载波动

**解决**：
```bash
# 关闭其他应用
# 多次运行取平均值
pytest tests/performance/test_benchmarks.py --count=5
```

#### Q2: 内存测试失败

**原因**：Python 垃圾回收时机不确定

**解决**：
```python
# 在测试中手动触发 GC
import gc
gc.collect()
```

#### Q3: 并发测试超时

**原因**：线程调度延迟

**解决**：
```bash
# 增加超时阈值
pytest tests/performance/test_concurrency.py -v --timeout=30
```

### 调试技巧

1. **添加详细日志**：
   ```bash
   pytest tests/performance/ -v -s --log-cli-level=INFO
   ```

2. **性能分析**：
   ```bash
   pytest tests/performance/ --profile-svg=profile.svg
   ```

3. **内存分析**：
   ```bash
   pytest tests/performance/test_memory_efficiency.py --memray
   ```

## 📞 获取帮助

### 文档资源

- [pytest 文档](https://docs.pytest.org/)
- [pytest-benchmark 文档](https://pytest-benchmark.readthedocs.io/)
- [项目 README](../../../README.md)

### 联系方式

- 查看项目 ISSUE
- 提交性能问题报告
- 参与性能优化讨论

---

**最后更新**: 2026-03-30  
**维护者**: pytest-dynamic-params 团队
