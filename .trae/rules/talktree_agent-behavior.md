---
name: "talktree-agent-behavior"
description: "定义 TalkTree Agent 的对话导航和上下文管理行为规范"
---

# TalkTree Agent 行为规范

## 核心理念

**TalkTree 不是让 AI 更智能，而是让用户能够：**
- ✅ 在多个对话框之间灵活跳转
- ✅ 在一个对话框中的不同话题间切换
- ✅ 在一个话题下的不同问答结果间导航
- ✅ 准确继承和存储记忆
- ✅ 管理上下文状态

## 核心概念

### 对象层级

```
对话（Conversation）
└── 话题（Topic）
    └── 问答对（QAPair）
```

**每个对象都有唯一 ID**：
- 对话 ID：`conv_{uuid}`
- 话题 ID：`topic_{uuid}`
- 问答 ID：`qa_{uuid}`
- 快照 ID：`snap_{uuid}`

## 用户命令示例

### 话题管理命令

```
# 创建话题
创建话题 "装饰器应用"
  → 返回：✅ 已创建话题：装饰器应用 (ID: topic_xxxxx)

# 切换话题
切换到 "Python 基础"
  → 返回：✅ 已切换到话题：Python 基础 (ID: topic_xxxxx)

# 查看话题（支持 git log 风格的参数）
列出所有话题
  → 返回：话题树状图
tt topic ls -5
  → 返回：最近 5 个话题
tt topic ls --grep "装饰器"
  → 返回：包含"装饰器"的话题
```

### 问答对管理

```
# 每个问答对自动获得 ID
用户：什么是装饰器？
AI: 装饰器是... (ID: qa_xxxxx)

# 查看历史（支持 git log 风格参数）
列出问答对
  → 返回：问答对树状图
tt qa ls -10
  → 返回：最近 10 轮问答
tt qa ls --grep "@"
  → 返回：包含"@"的问答
```

### 快照管理

```
# 保存快照
保存快照 "装饰器理论完成"
  → 返回：✅ 快照已保存 (ID: snap_xxxxx)

# 恢复快照
恢复到快照 "装饰器理论完成"
  → 使用快照 ID 或名称恢复

# 查看快照（支持 git log 风格参数）
列出快照
  → 返回：快照树状图
tt snap ls -5 --grep "阶段"
  → 返回：最近 5 个包含"阶段"的快照
```

## 自动保存触发条件

以下操作会自动保存和记录历史：

1. **创建话题**
   - 保存 conversation.json
   - 保存新话题文件
   - 记录 changelog
   - 生成历史文件

2. **添加问答对**
   - 更新话题文件
   - 更新 conversation.json
   - 记录 changelog
   - 每 10 轮生成历史文件

3. **切换话题**
   - 更新 conversation.json
   - 记录 changelog

4. **保存快照**
   - 保存快照文件
   - 记录 changelog
   - 生成历史文件

5. **定时保存**
   - 每 900 秒（15 分钟）自动保存一次
   - 生成历史文件
   - 时间间隔可在 talktree-config/config.yaml 中配置

## 与其他规则的配合

- 配合 [`talktree-command-rules.md`](talktree-command-rules.md) - 使用通用命令规则
- 配合 [`talktree-topic-management.md`](talktree-topic-management.md) - 提供话题管理功能
- 配合 [`talktree-memory-inheritance.md`](talktree-memory-inheritance.md) - 定义记忆继承规则

## 版本

- **版本**: 2.2.0
- **创建日期**: 2026-03-26
- **最后更新**: 2026-03-31
- **维护者**: TalkTree Team
