# TalkTree 系统总览

> **让人机对话灵活导航**  
> *Navigate conversations with Ease*

## 核心功能

| 功能 | 命令示例 | 说明 |
|------|---------|------|
| 对话管理 | `tt conv ls` | 列出所有对话 |
| 话题管理 | `tt topic ls -5` | 列出最近 5 个话题 |
| 问答导航 | `tt qa ls --grep "xxx"` | 搜索问答 |
| 快照管理 | `tt snap save "名称"` | 保存状态 |
| 记忆管理 | `tt mem ls` | 查看记忆 |

## 核心特性

- ✅ **唯一 ID** - 每个对象都有唯一标识（conv_xxx、topic_xxx、qa_xxx、snap_xxx）
- ✅ **自动保存** - 状态自动持久化到文件，无需手动操作
- ✅ **话题隔离** - 每个话题独立管理上下文，不会混淆
- ✅ **记忆继承** - 子话题选择性继承父话题的核心概念和知识
- ✅ **历史导航** - 浏览和跳转到任意历史问答对
- ✅ **快照管理** - 保存和恢复重要节点状态

## 系统简介

**TalkTree** 是一套**对话导航和上下文管理系统**。它不是为了让 AI 更智能（AI 已经具备智能处理能力），而是为了解决长对话中的核心痛点：

### 🎯 核心问题

在使用 AI 进行长对话时，你是否遇到过：

- ❌ 同时讨论多个话题，上下文混杂在一起
- ❌ 想回到之前的某个话题，但找不到
- ❌ 开启新话题后，之前的上下文丢失了
- ❌ 需要在不同话题间切换，但 AI 记不住
- ❌ 长对话后迷失了方向，不知道在哪

### ✨ TalkTree 的解决方案

- ✅ **话题管理** - 为不同话题创建独立空间
- ✅ **灵活切换** - 在话题间自由跳转
- ✅ **上下文保存** - 每个话题独立保存上下文
- ✅ **记忆继承** - 子话题选择性继承父话题记忆
- ✅ **历史导航** - 浏览和跳转到任意历史问答
- ✅ **快照管理** - 保存和恢复重要节点

## 核心特性

### 1. 唯一 ID 系统

**所有对象都有唯一 ID**：

```
对话 ID: conv_550e8400-e29b-41d4-a716-446655440000
话题 ID: topic_550e8400-e29b-41d4-a716-446655440000
问答 ID: qa_550e8400-e29b-41d4-a716-446655440000
快照 ID: snap_550e8400-e29b-41d4-a716-446655440000
```

**用途**：
- 🔍 精确定位和引用
- 🔗 对象间关联
- 📋 历史记录追踪
- 💾 文件存储索引

### 2. 自动文件持久化

**自动保存到文件**：

```
talktree-conversations/
└── conv_xxxxx/
    ├── conversation.json          # 对话主文件
    ├── changelog.json             # 变更记录
    ├── topics/
    │   ├── topic_001.json         # 话题 1
    │   └── topic_002.json         # 话题 2
    └── history/
        ├── 20260326_143022_history.md  # 历史记录 1
        └── 20260326_150045_history.md  # 历史记录 2
```

**自动保存触发**：
- 创建话题时
- 添加问答对时
- 切换话题时
- 保存快照时
- 每 15 分钟定时保存

### 3. 历史记录

**自动生成 Markdown 格式的历史文件**，方便用户翻看和搜索。

## 核心组件

### 规则文件

| 文件 | 职责 |
|------|------|
| [`rules/talktree-agent-behavior.md`](rules/talktree-agent-behavior.md) | 定义对话导航和上下文管理的行为规范 |
| [`rules/talktree-topic-management.md`](rules/talktree-topic-management.md) | 定义话题树的组织规则和管理规则 |
| [`rules/talktree-memory-inheritance.md`](rules/talktree-memory-inheritance.md) | 定义记忆分层和继承规则 |
| [`rules/talktree-persistence.md`](rules/talktree-persistence.md) | 定义文件存储结构和保存规则 |

### 技能文件

| 文件 | 职责 |
|------|------|
| [`skills/talktree-context-navigator/SKILL.md`](skills/talktree-context-navigator/SKILL.md) | 上下文导航技能，支持话题切换、历史浏览、快照管理 |
| [`skills/talktree-topic-manager/SKILL.md`](skills/talktree-topic-manager/SKILL.md) | 话题管理技能，创建、删除、合并话题 |
| [`skills/talktree-memory-manager/SKILL.md`](skills/talktree-memory-manager/SKILL.md) | 记忆管理技能，管理记忆存储和继承 |
| [`skills/talktree-persistence/SKILL.md`](skills/talktree-persistence/SKILL.md) | 持久化技能，实现文件保存和历史生成 |

## 命令参考

TalkTree 使用类似 bash/git 的简洁命令风格：

```bash
# 对话命令
tt conv new <name>              # 创建对话
tt conv ls                      # 列出对话
tt conv use <id_or_name>        # 切换对话
tt conv rm <id_or_name>         # 删除对话

# 话题命令
tt topic new <name> [-p <parent>]   # 创建话题
tt topic use <name_or_id>           # 切换话题
tt topic ls [参数]                  # 列出话题树（支持 git log 风格的参数）
tt topic rm <name_or_id>            # 删除话题
tt topic merge <t1> <t2>            # 合并话题

# 问答对命令
tt qa ls [参数]                     # 查看问答对历史（支持 git log 风格的参数）
tt qa use <qa_id>                   # 切换问答对
tt qa rm <qa_id>                    # 删除问答对

# 快照命令
tt snap save <name>                 # 保存快照
tt snap use <name_or_id>            # 使用/恢复快照
tt snap ls [参数]                   # 列出快照（支持 git log 风格的参数）
tt snap rm <name_or_id>             # 删除快照

# 记忆命令
tt mem ls [参数]                    # 查看记忆（支持 git log 风格的参数）
tt mem add <key> <value>            # 添加记忆
tt mem rm <key>                     # 删除记忆
tt mem export <file>                # 导出记忆
tt mem import <file>                # 导入记忆
```

## 使用示例

### 创建话题树

```bash
# 创建学习对话
tt conv new "Python Learning"

# 创建根话题
tt topic new "Python Basics"

# 创建子话题
tt topic new "Variables" -p "Python Basics"
tt topic new "Functions" -p "Python Basics"
tt topic new "Decorators" -p "Functions"

# 查看所有话题
tt topic ls
```

### 切换话题

```bash
# 切换到子话题
tt topic use "Variables"

# 开始对话
用户：什么是变量？
AI: 变量是存储数据的容器...
    **问答 ID**: `qa_xxxxx`
    💾 已自动保存

# 切换到另一个子话题
tt topic use "Functions"
# 自动保存 "Variables" 的状态，加载 "Functions" 的上下文
```

### 历史导航

```bash
# 查看问答对历史
tt qa ls

# 搜索问答对
tt qa ls --grep "变量"

# 使用特定问答对
tt qa use qa_xxxxx

# 基于历史问答继续
用户：基于这个继续
```

### 快照管理

```bash
# 保存快照
tt snap save "variables-complete"

# 继续学习...

# 恢复到快照
tt snap load "variables-complete"
# 恢复到保存时的完整状态
```

### 记忆管理

```bash
# 查看记忆
tt mem ls

# 添加记忆
tt mem add "variable_def" "变量是存储数据的容器" --type core_concept

# 导出记忆
tt mem export "./memories.json"

# 导入记忆
tt mem import "./memories.json"
```

## 配置说明

详细的配置指南请查看：
- [`talktree-config/config.yaml`](talktree-config/config.yaml) - 主配置文件
- [`talktree-config/CONFIG_GUIDE.md`](talktree-config/CONFIG_GUIDE.md) - 配置使用指南

### 常用配置

```yaml
# 存储设置
storage_path: "{AI_ROOT}/talktree-conversations"   # 存储根路径
auto_save_interval: 900           # 自动保存间隔（秒，900=15 分钟）
auto_save_enabled: true           # 启用自动保存

# ID 生成设置
use_short_id: false               # 使用短 ID（8 字符）而非完整 UUID
id_prefixes:
  conversation: "conv_"           # 对话 ID 前缀
  topic: "topic_"                 # 话题 ID 前缀
  qa_pair: "qa_"                  # 问答对 ID 前缀
  snapshot: "snap_"               # 快照 ID 前缀

# 记忆管理设置
memory_inheritance_strategy: "default"  # 记忆继承策略：default, all, selective, none
short_term_memory_turns: 10            # 短期记忆保留轮数

# 显示设置
show_ids_in_response: true        # 在响应中显示 ID
```

## 核心优势

### ✅ 唯一标识
- 每个对象都有唯一 ID
- 支持精确定位和引用
- 便于文件存储和检索

### ✅ 自动保存
- 状态变更自动保存
- 无需手动操作
- 数据安全可靠

### ✅ 历史记录
- 自动生成 Markdown 历史
- 方便用户翻看
- 支持搜索和定位

### ✅ 话题隔离
- 不同话题上下文隔离
- 不会混淆
- 支持灵活切换

### ✅ 记忆继承
- 子话题选择性继承父话题记忆
- 支持多种继承策略
- 保持知识传承

## 文件结构

```
{AI_ROOT}/                       # AI 根目录（如 .trae/、.codebuddy/ 等）
├── talktree-config/
│   ├── config.yaml            # 主配置文件
│   └── CONFIG_GUIDE.md        # 配置指南
│
├── rules/
│   ├── talktree-agent-behavior.md       # Agent 行为规范
│   ├── talktree-config-reference.md     # 配置引用
│   ├── talktree-document-priority.md    # 文档优先级规则
│   ├── talktree-topic-management.md     # 话题管理规则
│   ├── talktree-memory-inheritance.md   # 记忆继承规则
│   └── talktree-persistence.md          # 持久化规则
│
├── skills/
│   ├── talktree-context-navigator/
│   │   └── SKILL.md           # 上下文导航技能
│   ├── talktree-topic-manager/
│   │   └── SKILL.md           # 话题管理技能
│   ├── talktree-memory-manager/
│   │   └── SKILL.md           # 记忆管理技能
│   └── talktree-persistence/
│       └── SKILL.md           # 持久化技能
│
├── talktree-specs/
│   └── 需求.md                # 需求规格文档
│
├── talktree-README.md                   # 系统总览（本文件）
└── talktree-project.md                  # 项目结构说明
```

**注意**：`{AI_ROOT}` 是占位符，实际使用时替换为当前 AI 的根目录（如 `.trae/`、`.codebuddy/` 等）

**运行时生成的文件结构**：

```
{AI_ROOT}/talktree-conversations/           # 对话数据存储（运行时生成）
└── conv_xxxxx/
    ├── conversation.json          # 对话主文件
    ├── changelog.json             # 变更记录
    ├── topics/
    │   ├── topic_001.json         # 话题文件
    │   └── ...
    └── history/
        ├── 20260326_143022_history.md
        └── ...
```

## 快速开始

### 1. 创建对话

```
# 自动创建对话并返回 ID
AI: 好的，我们开始新的对话
    **对话 ID**: `conv_xxxxx`
```

### 2. 创建话题

```
用户：创建话题 "Python 基础"

AI: ✅ 已创建话题：Python 基础
    **ID**: `topic_xxxxx`
```

### 3. 开始对话

```
用户：什么是变量？

AI: 变量是存储数据的容器...
    **问答 ID**: `qa_xxxxx`
    
    💾 已自动保存
```

### 4. 查看历史

```
用户：查看历史

AI: ## 历史问答
    
    ### 第 1 轮 (ID: `qa_xxxxx`)
    **用户**: 什么是变量？
    **AI**: 变量是...
```

### 5. 保存快照

```
用户：保存快照 "变量学习完成"

AI: ✅ 快照已保存
    **快照 ID**: `snap_xxxxx`
    
    📄 历史记录已生成
```

## 版本

- **版本**: 1.0.0
- **创建日期**: 2026-03-26
- **最后更新**: 2026-03-26
- **维护者**: TalkTree Team

## 许可证

MIT License

---

**TalkTree** - 让人机对话灵活导航  
*Navigate conversations with Ease* 🧭
