---
name: "talktree-conversation-manager"
description: "TalkTree 对话管理技能，用于创建、切换和管理多个对话"
---

# TalkTree 对话管理技能

## 职责

- 📁 **对话管理** - 创建、删除、切换对话
- 📋 **对话列表** - 列出所有对话
- 🔀 **对话合并** - 合并两个对话
- 📤 **对话导出** - 导出对话到文件
- 📥 **对话导入** - 从文件导入对话

## 命令定义

### tt conv new

**功能**：创建新对话

**语法**：
```bash
tt conv new <name>
```

**AI 应实现**：
1. 生成对话 ID（`conv_{uuid}`）
2. 创建对话对象
3. 初始化元数据
4. 保存到文件

**输出格式**：
```
✅ 已创建对话
💾 conv_{id}: {name} | {topics}话题 {snapshots}快照 {memories}记忆
```

### tt conv ls

**功能**：列出所有对话

**语法**：
```bash
tt conv ls [参数]
```

**参数**（参考 git log 风格）：
- 必须使用 git log 风格（`-5`、`--grep "xxx"` 等）
- AI 应理解等价形式：`-5`、`-n 5`、`--limit 5`；`--grep`、`-g`
- 参数可以组合使用

**AI 应实现**：
1. 智能解析参数
2. 按参数执行
3. 构建树状结构
4. 显示树状图

**输出格式**：
```
**对话列表**
📍 当前：conv_{id}: {name}
📊 共 {count} 个对话

📁 conv_{id}: {name}
    ├── topic_{id}: {name}
    │   └── qa_{id} | {问题摘要}
```

### tt conv use

**功能**：切换到指定对话

**语法**：
```bash
tt conv use <conv_id_or_name> [新问题]
```

**AI 应实现**：
1. 查找对话
2. 保存当前对话状态
3. 加载新对话上下文
4. 如果有新问题，直接回答
5. 记录状态变更

**输出格式**：
```
✅ 已切换到对话并回答
📎 conv_{id}: {name}
💾 conv_{id}/topic_{id}/qa_{id} | {问题}
```

### tt conv rm

**功能**：删除对话

**语法**：
```bash
tt conv rm <conv_id_or_name>
```

**AI 应实现**：
1. 检查对话存在且非当前对话
2. 删除对话文件
3. 从列表中移除
4. 记录变更

### tt conv merge

**功能**：合并两个对话

**语法**：
```bash
tt conv merge <conv1> <conv2>
```

**AI 应实现**：
1. 迁移话题
2. 合并记忆
3. 删除源对话
4. 保存

### tt conv export

**功能**：导出对话到文件

**语法**：
```bash
tt conv export <conv_id> [file_path]
```

**AI 应实现**：
1. 序列化对话
2. 写入文件

### tt conv import

**功能**：从文件导入对话

**语法**：
```bash
tt conv import <file_path>
```

**AI 应实现**：
1. 读取文件
2. 反序列化对话
3. 添加到对话列表
4. 保存

## 协作关系

- 调用 **persistence** - 保存对话到文件
- 调用 **topic-manager** - 管理话题
- 调用 **snapshot-manager** - 管理快照
- 被 **context-navigator** 调用 - 提供对话切换

## 版本

- **版本**: 2.0.0
- **创建日期**: 2026-03-27
- **维护者**: TalkTree Team
