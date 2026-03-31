# TalkTree 配置指南

## 快速开始

### 1. 配置文件位置

```
talktree-config
└── config.yaml          # 主配置文件
```

### 2. 常用配置

#### 修改自动保存间隔

```yaml
# 默认：900 秒 = 15 分钟
auto_save_interval: 900

# 改为 5 分钟
auto_save_interval: 300

# 改为 30 分钟
auto_save_interval: 1800
```

#### 修改存储路径

```yaml
# 默认：./talktree-conversations
storage_path: "./talktree-conversations"

# 改为其他位置
storage_path: "D:/talktree-conversations"
```

#### 显示/隐藏 ID

```yaml
# 显示 ID（推荐）
show_ids_in_response: true

# 隐藏 ID
show_ids_in_response: false
```

### 3. 配置生效

修改配置文件后**自动生效**，无需重启。

## 完整配置项

### 基础配置

| 配置项 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `auto_save_interval` | 自动保存间隔（秒） | 900 | 300, 900, 1800 |
| `auto_save_enabled` | 是否启用自动保存 | true | true, false |
| `generate_history_markdown` | 生成 Markdown 历史 | true | true, false |
| `history_markdown_interval` | Markdown 历史间隔（秒） | 600 | 300, 600, 900 |
| `storage_path` | 存储路径 | "./talktree-conversations" | "D:/Data" |
| `use_relative_path` | 使用相对路径 | true | true, false |
| `file_encoding` | 文件编码 | "utf-8" | "utf-8", "gbk" |
| `json_indent` | JSON 缩进空格 | 2 | 2, 4 |

### ID 配置

| 配置项 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `use_short_id` | 使用短 ID（8 位） | false | true, false |
| `id_prefixes.conversation` | 对话 ID 前缀 | "conv_" | "conv_", "c_" |
| `id_prefixes.topic` | 话题 ID 前缀 | "topic_" | "topic_", "t_" |
| `id_prefixes.qa_pair` | 问答 ID 前缀 | "qa_" | "qa_", "q_" |
| `id_prefixes.snapshot` | 快照 ID 前缀 | "snap_" | "snap_", "s_" |

### 记忆配置

| 配置项 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `memory_inheritance_strategy` | 记忆继承策略 | "default" | "default", "all", "none" |
| `short_term_memory_turns` | 短期记忆轮数 | 10 | 5, 10, 20 |
| `long_term_memory_enabled` | 启用长期记忆 | true | true, false |

### 性能配置

| 配置项 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `context_window_size` | 上下文窗口大小 | 10 | 10, 20, 50 |
| `context_compression_enabled` | 启用上下文压缩 | true | true, false |
| `context_compression_threshold` | 压缩阈值 | 20 | 20, 50, 100 |

### 显示配置

| 配置项 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `show_ids_in_response` | 显示 ID | true | true, false |
| `show_timestamps` | 显示时间戳 | false | true, false |
| `show_save_notifications` | 显示保存提示 | true | true, false |
| `default_history_limit` | 默认历史轮数 | 10 | 10, 20, 50 |

### 日志配置

| 配置项 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `log_level` | 日志级别 | "INFO" | "DEBUG", "INFO", "WARNING" |
| `log_file_path` | 日志文件路径 | "./logs/TalkTree.log" | "./logs/app.log" |
| `log_rotation_enabled` | 启用日志轮转 | true | true, false |
| `log_max_size_mb` | 日志最大大小（MB） | 10 | 10, 50, 100 |
| `log_backup_count` | 保留日志数量 | 5 | 3, 5, 10 |

## 配置场景

### 场景 1：开发调试

```yaml
# 快速保存，详细日志
auto_save_interval: 60          # 1 分钟保存
generate_history_markdown: true
show_ids_in_response: true
show_timestamps: true
show_save_notifications: true
log_level: "DEBUG"
```

### 场景 2：日常使用

```yaml
# 标准配置
auto_save_interval: 900         # 15 分钟保存
generate_history_markdown: true
show_ids_in_response: true
show_timestamps: false
show_save_notifications: true
log_level: "INFO"
```

### 场景 3：生产环境

```yaml
# 高性能，简洁输出
auto_save_interval: 1800        # 30 分钟保存
generate_history_markdown: true
show_ids_in_response: true
show_timestamps: false
show_save_notifications: false
log_level: "WARNING"
```

### 场景 4：长对话优化

```yaml
# 大型对话优化
auto_save_interval: 1800        # 30 分钟保存
context_window_size: 20
context_compression_enabled: true
context_compression_threshold: 50
short_term_memory_turns: 20
```

### 场景 5：简洁模式

```yaml
# 简洁输出
auto_save_interval: 900
show_ids_in_response: false
show_timestamps: false
show_save_notifications: false
default_history_limit: 5
```

## 配置示例

### 最小配置

```yaml
# 只配置必要的参数
auto_save_interval: 900
storage_path: "{AI_ROOT}/talktree-conversations"
```

### 推荐配置

```yaml
# 推荐配置（平衡性能和功能）
auto_save_interval: 900
auto_save_enabled: true
generate_history_markdown: true
history_markdown_interval: 600
storage_path: "{AI_ROOT}/talktree-conversations"
show_ids_in_response: true
show_timestamps: false
show_save_notifications: true
log_level: "INFO"
context_window_size: 10
memory_inheritance_strategy: "default"
```

### 完整配置

```yaml
# 完整配置（所有选项）
auto_save_interval: 900
auto_save_enabled: true
generate_history_markdown: true
history_markdown_interval: 600
storage_path: "{AI_ROOT}/talktree-conversations"
use_relative_path: true
file_encoding: "utf-8"
json_indent: 2

id_prefixes:
  conversation: "conv_"
  topic: "topic_"
  qa_pair: "qa_"
  snapshot: "snap_"

use_short_id: false

memory_inheritance_strategy: "default"
short_term_memory_turns: 10
long_term_memory_enabled: true

context_window_size: 10
context_compression_enabled: true
context_compression_threshold: 20

show_ids_in_response: true
show_timestamps: false
show_save_notifications: true
default_history_limit: 10

log_level: "INFO"
log_file_path: "./logs/TalkTree.log"
log_rotation_enabled: true
log_max_size_mb: 10
log_backup_count: 5
```

## 常见问题

### Q1: 如何禁用自动保存？

```yaml
auto_save_enabled: false
```

### Q2: 如何更改存储位置？

```yaml
storage_path: "D:/talktree-conversations"
```

### Q3: 如何不显示 ID？

```yaml
show_ids_in_response: false
```

### Q4: 如何加快保存频率？

```yaml
auto_save_interval: 60  # 1 分钟
```

### Q5: 如何禁用 Markdown 历史？

```yaml
generate_history_markdown: false
```

### Q6: 配置文件在哪里？

```
./talktree-config/config.yaml
```

### Q7: 配置错误了怎么办？

删除或重命名 `talktree-config/config.yaml` 文件，系统将使用默认配置。

### Q8: 如何验证配置是否正确？

确保 YAML 格式正确：
- 使用冒号 `:` 分隔键值
- 使用空格缩进（不要用 Tab）
- 列表使用 `-` 开头

## 配置优先级

1. **代码中的默认值** - 最低优先级
2. **配置文件** - 中等优先级
3. **运行时参数** - 最高优先级（如果支持）

## 配置变更历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.0.0 | 2026-03-26 | 初始版本，支持所有配置项 |

## 技术支持

如有问题，请查看：
- [`{AI_ROOT}/talktree-README.md`](../talktree-README.md) - 系统总览
- [`{AI_ROOT}/rules/talktree-agent-behavior.md`](../rules/talktree-agent-behavior.md) - 行为规范

---

**TalkTree** - 让人机对话灵活导航  
*Navigate conversations with Ease* 🧭
