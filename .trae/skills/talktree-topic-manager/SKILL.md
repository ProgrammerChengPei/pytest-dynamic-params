---
name: "talktree-topic-manager"
description: "TalkTree topic management skill for creating, switching, and managing topic trees"
---

# TalkTree Topic Manager Skill

## 职责

- 🌳 **话题树管理** - 创建、删除、合并话题
- 🔄 **话题切换** - 在不同话题间灵活切换
- 🔗 **关系维护** - 维护话题间的父子关系
- 💾 **自动保存** - 所有操作自动保存到文件

## 命令定义

### tt topic new

**功能**：创建新话题

**语法**：
```bash
tt topic new <name> [-p <parent_topic>]
```

**参数**：
- `<name>` - 话题名称（必需）
- `-p, --parent` - 父话题名称或 ID（可选，默认为根话题）

**执行步骤**：
```python
async def topic_new(name: str, parent: str = None):
    # 1. 验证话题名称不重复
    if topic_exists_in_current_parent(name):
        return error(f"话题已存在：{name}")
    
    # 2. 确定父话题
    if parent:
        parent_topic = find_topic(parent)
        if not parent_topic:
            return error(f"父话题不存在：{parent}")
    else:
        parent_topic = get_root_topic()
    
    # 3. 生成唯一 ID
    topic_id = generate_uuid(prefix="topic_")
    
    # 4. 创建话题对象
    new_topic = Topic(
        id=topic_id,
        name=name,
        parent_id=parent_topic.id,
        created_at=datetime.now()
    )
    
    # 5. 建立父子关系
    parent_topic.children_ids.append(topic_id)
    
    # 6. 继承记忆（根据策略）
    inherited_count = inherit_memory(new_topic, parent_topic)
    
    # 7. 保存到文件
    await save_topic(new_topic)
    await save_conversation(conversation)
    
    # 8. 返回结果
    return success(f"""
✅ 已创建新话题：{name}
**ID**: `{topic_id}`
父话题：{parent_topic.name} (ID: `{parent_topic.id}`)
继承记忆：{inherited_count} 条
创建时间：{new_topic.created_at.strftime('%Y-%m-%d %H:%M:%S')}

💾 已自动保存到文件
""")
```

**示例**：
```bash
# 创建根话题
tt topic new "Python Learning"

# 创建子话题
tt topic new "Decorators" -p "Python Learning"

# 使用 ID 指定父话题
tt topic new "Advanced" -p "topic_xxxxx"
```

### tt topic use

**功能**：切换到指定话题

**语法**：
```bash
tt topic use <name_or_id>
```

**执行步骤**：
```python
async def topic_use(identifier: str):
    # 1. 查找话题
    target_topic = find_topic(identifier)
    if not target_topic:
        return error(f"话题不存在：{identifier}")
    
    # 2. 保存当前话题状态
    await save_current_topic()
    
    # 3. 记录原话题 ID
    from_topic_id = current_topic.id
    
    # 4. 切换话题
    old_topic = current_topic
    current_topic = target_topic
    
    # 5. 加载新话题上下文
    await load_topic_context(target_topic)
    
    # 6. 记录状态变更
    record_change(
        type="topic_switched",
        details={
            "from_topic_id": from_topic_id,
            "to_topic_id": target_topic.id
        }
    )
    
    # 7. 保存
    await save_conversation(conversation)
    
    # 8. 返回结果
    return success(f"""
✅ 已切换到话题：{target_topic.name}
**ID**: `{target_topic.id}`
问答数：{len(target_topic.qa_pairs)}
记忆数：{len(target_topic.memory)}

💾 已记录状态变更
""")
```

**示例**：
```bash
# 使用名称切换
tt topic use "Decorators"

# 使用 ID 切换
tt topic use "topic_xxxxx"
```

### tt topic ls

**功能**：列出所有话题

**语法**：
```bash
tt topic ls
```

**执行步骤**：
```python
async def topic_ls():
    # 1. 获取所有话题
    topics = get_all_topics()
    
    # 2. 构建树状结构
    tree = build_topic_tree(topics)
    
    # 3. 生成输出
    output = ["## 话题列表\n"]
    output.append(f"**对话 ID**: `{conversation.id}`")
    output.append(f"**总话题数**: {len(topics)}\n")
    
    # 4. 遍历树
    for topic in tree:
        marker = "📍" if topic.id == current_topic.id else "📁"
        indent = "   " * topic.depth
        
        output.append(f"{indent}{marker} **{topic.name}** (ID: `{topic.id}`)")
        output.append(f"{indent}   问答数：{len(topic.qa_pairs)}")
        output.append(f"{indent}   记忆数：{len(topic.memory)}")
        
        if topic.parent_id:
            output.append(f"{indent}   父话题：{topic.parent_name}")
        
        output.append("")
    
    return "\n".join(output)
```

**示例**：
```bash
tt topic ls
```

**输出**：
```
## 话题列表

**对话 ID**: `conv_xxxxx`
**总话题数**: 5

📍 **当前话题** (ID: `topic_yyyyy`)
   问答数：10
   记忆数：8
   父话题：Python Basics

📁 **Python Basics** (ID: `topic_xxxxx`)
   问答数：15
   记忆数：12
   父话题：根话题

📁 **Advanced** (ID: `topic_zzzzz`)
   问答数：5
   记忆数：3
   父话题：Python Basics
```

### tt topic rm

**功能**：删除话题

**语法**：
```bash
tt topic rm <name_or_id>
```

**执行步骤**：
```python
async def topic_rm(identifier: str):
    # 1. 查找话题
    target_topic = find_topic(identifier)
    if not target_topic:
        return error(f"话题不存在：{identifier}")
    
    # 2. 检查是否为当前话题
    if target_topic.id == current_topic.id:
        return error("""
❌ 无法删除激活的话题

💡 建议：先切换到其他话题再删除
可用命令：tt topic use <other_topic>
""")
    
    # 3. 递归删除子话题
    deleted_children = []
    for child_id in target_topic.children_ids:
        child_topic = get_topic(child_id)
        deleted_children.append(child_topic.name)
        delete_topic_recursive(child_topic)
    
    # 4. 从父话题移除
    if target_topic.parent_id:
        parent_topic = get_topic(target_topic.parent_id)
        parent_topic.children_ids.remove(target_topic.id)
    
    # 5. 从对话索引移除
    del conversation.topics[target_topic.id]
    
    # 6. 记录变更
    record_change(
        type="topic_deleted",
        object_id=target_topic.id,
        details={
            "name": target_topic.name,
            "children_deleted": deleted_children
        }
    )
    
    # 7. 保存
    await save_conversation(conversation)
    
    # 8. 返回结果
    return success(f"""
✅ 已删除话题：{target_topic.name}
**ID**: `{target_topic.id}`
同时删除子话题：{len(deleted_children)} 个

💾 已保存到文件
""")
```

**示例**：
```bash
tt topic rm "Old Topic"
tt topic rm "topic_xxxxx"
```

### tt topic merge

**功能**：合并两个话题

**语法**：
```bash
tt topic merge <topic1> <topic2>
```

**执行步骤**：
```python
async def topic_merge(topic1_id: str, topic2_id: str):
    # 1. 查找两个话题
    topic1 = find_topic(topic1_id)
    topic2 = find_topic(topic2_id)
    
    if not topic1 or not topic2:
        return error("话题不存在")
    
    if topic1.id == topic2.id:
        return error("无法合并相同话题")
    
    # 2. 迁移问答对
    migrated_count = 0
    for qa in topic2.qa_pairs:
        topic1.qa_pairs.append(qa)
        migrated_count += 1
    
    # 3. 合并记忆
    merged_memory_count = 0
    for key, memory in topic2.memory.items():
        if key not in topic1.memory:
            topic1.memory[key] = memory
            merged_memory_count += 1
    
    # 4. 迁移子话题
    for child_id in topic2.children_ids:
        child = get_topic(child_id)
        child.parent_id = topic1.id
        topic1.children_ids.append(child_id)
    
    # 5. 删除源话题
    await topic_rm(topic2.id)
    
    # 6. 保存目标话题
    await save_topic(topic1)
    
    # 7. 返回结果
    return success(f"""
✅ 已合并话题
目标话题：{topic1.name} (ID: `{topic1.id}`)
源话题：{topic2.name} (ID: `{topic2.id}`)
迁移问答：{migrated_count} 条
合并记忆：{merged_memory_count} 条
""")
```

**示例**：
```bash
tt topic merge "Python Basics" "Old Basics"
```

## 数据结构

```python
class Topic:
    id: str                    # 唯一 ID (topic_{uuid})
    name: str                  # 话题名称
    parent_id: str | None      # 父话题 ID
    children_ids: list[str]    # 子话题 ID 列表
    qa_pairs: list[QAPair]     # 问答对列表
    memory: dict               # 记忆字典
    snapshots: list[Snapshot]  # 快照列表
    metadata: dict             # 元数据

class TopicTree:
    root_topics: list[Topic]   # 根话题列表
    
    def build_tree(self, topics: list[Topic]):
        """构建树状结构"""
        topic_map = {t.id: t for t in topics}
        
        for topic in topics:
            if topic.parent_id:
                parent = topic_map.get(topic.parent_id)
                if parent:
                    topic.depth = parent.depth + 1
            else:
                topic.depth = 0
```

## 协作关系

- 调用 **persistence** - 保存话题到文件
- 调用 **memory-manager** - 实现记忆继承
- 被 **context-navigator** 调用 - 提供话题导航

## 版本

- **版本**: 1.0.0
- **创建日期**: 2026-03-26
- **维护者**: TalkTree Team
