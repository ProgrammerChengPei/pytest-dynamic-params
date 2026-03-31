# TalkTree 配置引用

## 配置文件位置

TalkTree 的配置文件位于：

```
{AI_ROOT}/talktree-config/
├── config.yaml            # 主配置文件
└── CONFIG_GUIDE.md        # 配置使用指南
```

**注意**：`{AI_ROOT}` 表示当前 AI 的根目录（如 `.trae/`、`.codebuddy/` 等），实际使用时替换为对应的目录名。

## 重要配置项

### 存储设置
```yaml
storage_path: "./talktree-conversations"   # 存储根路径
auto_save_interval: 900           # 自动保存间隔（秒，900=15 分钟）
auto_save_enabled: true           # 启用自动保存
```

### ID 生成设置
```yaml
id_prefixes:
  conversation: "conv_"           # 对话 ID 前缀
  topic: "topic_"                 # 话题 ID 前缀
  qa_pair: "qa_"                  # 问答对 ID 前缀
  snapshot: "snap_"               # 快照 ID 前缀
```

### 记忆管理设置
```yaml
memory_inheritance_strategy: "default"  # 记忆继承策略
short_term_memory_turns: 10            # 短期记忆保留轮数
```

## AI 行为要求

当用户提到配置、设置、参数时，AI 应该：

1. **引用配置文件** - 告知用户可以在 `{AI_ROOT}/talktree-config/config.yaml` 中修改配置
2. **使用配置值** - 在执行操作时使用配置文件中的值
3. **解释配置项** - 根据 `CONFIG_GUIDE.md` 解释各配置项的含义

## 命令示例

```bash
# 查看当前配置
tt config show

# 修改配置（通过编辑文件）
# 文件位置：{AI_ROOT}/talktree-config/config.yaml
```

## 版本

- **版本**: 1.0.0
- **创建日期**: 2026-03-26
- **维护者**: TalkTree Team
