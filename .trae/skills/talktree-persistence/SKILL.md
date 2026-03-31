---
name: "talktree-persistence"
description: "TalkTree persistence skill for auto-saving state to files and generating history"
---

# TalkTree Persistence Skill

## 职责

- 💾 **文件保存** - 保存对话、话题、记忆到 JSON 文件
- 📄 **历史记录** - 生成 Markdown 格式的历史记录
- 📝 **变更记录** - 记录所有状态变更
- ⏰ **定时保存** - 每 15 分钟自动保存

## 文件结构

```
talktree-conversations/
└── {conv_id}/
    ├── conversation.json      # 对话主文件
    ├── changelog.json         # 变更记录
    ├── topics/
    │   └── {topic_id}.json    # 话题文件
    └── history/
        └── {timestamp}_history.md  # 历史记录
```

## 保存触发条件

### 立即保存

| 操作 | 保存内容 |
|------|---------|
| 创建话题 | conversation.json + topic 文件 |
| 添加问答对 | topic 文件 + changelog |
| 切换话题 | conversation.json + changelog |
| 保存快照 | snapshot 文件 + topic 文件 |
| 删除话题 | conversation.json + changelog |
| 修改记忆 | topic 文件 |

### 定时保存

**间隔**：每 15 分钟（900 秒）

**保存内容**：
- conversation.json
- 所有话题文件
- changelog.json
- 生成历史记录 Markdown

## 核心函数

### save_conversation

```python
async def save_conversation(conv: Conversation):
    """保存对话主文件"""
    
    # 1. 目录准备
    conv_dir = os.path.join(storage_path, conv.id)
    os.makedirs(conv_dir, exist_ok=True)
    
    # 2. 序列化
    data = conv.to_dict()
    
    # 3. 写入临时文件
    temp_file = os.path.join(conv_dir, "conversation.tmp")
    target_file = os.path.join(conv_dir, "conversation.json")
    
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # 4. 验证 JSON
    with open(temp_file, 'r', encoding='utf-8') as f:
        json.load(f)  # 验证格式
    
    # 5. 原子重命名
    os.replace(temp_file, target_file)
    
    # 6. 记录保存时间
    conv.metadata['last_saved'] = datetime.now()
```

### save_topic

```python
async def save_topic(topic: Topic):
    """保存话题文件"""
    
    conv_dir = get_conversation_dir()
    topics_dir = os.path.join(conv_dir, "topics")
    os.makedirs(topics_dir, exist_ok=True)
    
    filepath = os.path.join(topics_dir, f"{topic.id}.json")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(topic.to_dict(), f, indent=2, ensure_ascii=False)
```

### generate_history_markdown

```python
async def generate_history_markdown():
    """生成 Markdown 历史记录"""
    
    # 1. 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_history.md"
    
    conv_dir = get_conversation_dir()
    history_dir = os.path.join(conv_dir, "history")
    os.makedirs(history_dir, exist_ok=True)
    
    filepath = os.path.join(history_dir, filename)
    
    # 2. 生成内容
    content = []
    content.append("# 对话历史\n\n")
    content.append(f"**对话 ID**: `{conversation.id}`\n")
    content.append(f"**对话名称**: {conversation.name}\n")
    content.append(f"**创建时间**: {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
    content.append(f"**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    content.append(f"**话题总数**: {len(conversation.topics)}\n")
    content.append(f"**问答总数**: {sum(len(t.qa_pairs) for t in conversation.topics.values())}\n\n")
    
    # 3. 遍历话题
    for topic in conversation.topics.values():
        content.append(f"### 📁 {topic.name} (ID: `{topic.id}`)\n")
        
        if topic.parent_id:
            parent = conversation.topics.get(topic.parent_id)
            parent_name = parent.name if parent else "未知"
            content.append(f"- **父话题**: {parent_name}\n")
        else:
            content.append(f"- **父话题**: 根话题\n")
        
        content.append(f"- **问答数**: {len(topic.qa_pairs)}\n")
        content.append(f"- **记忆数**: {len(topic.memory)}\n\n")
        
        # 4. 添加问答历史
        if topic.qa_pairs:
            content.append("#### 问答历史\n\n")
            for i, qa in enumerate(topic.qa_pairs, 1):
                content.append(f"**第 {i} 轮** (ID: `{qa.id}`)\n")
                content.append(f"- **用户**: {qa.user_input}\n")
                content.append(f"- **AI**: {qa.agent_response[:200]}...\n")
                content.append(f"- **时间**: {qa.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        content.append("---\n\n")
    
    # 5. 写入文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(content)
    
    return filepath
```

### record_change

```python
def record_change(change_type: str, object_type: str, object_id: str, details: dict):
    """记录状态变更"""
    
    change = {
        "id": f"change_{len(changelog.changes) + 1:03d}",
        "timestamp": datetime.now().isoformat(),
        "type": change_type,
        "object_type": object_type,
        "object_id": object_id,
        "details": details
    }
    
    changelog.changes.append(change)
    
    # 保存 changelog
    save_changelog()
```

### save_changelog

```python
async def save_changelog():
    """保存变更记录"""
    
    conv_dir = get_conversation_dir()
    filepath = os.path.join(conv_dir, "changelog.json")
    
    data = {
        "conversation_id": conversation.id,
        "changes": changelog.changes
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
```

## 定时保存任务

```python
async def auto_save_task():
    """定时保存任务"""
    
    while auto_save_enabled:
        # 等待间隔时间
        await asyncio.sleep(auto_save_interval)
        
        try:
            # 保存对话
            await save_conversation(conversation)
            
            # 保存所有话题
            for topic in conversation.topics.values():
                await save_topic(topic)
            
            # 保存 changelog
            await save_changelog()
            
            # 生成历史记录
            if generate_history_markdown_enabled:
                await generate_history_markdown()
            
            log.info(f"自动保存完成：{datetime.now()}")
            
        except Exception as e:
            log.error(f"自动保存失败：{e}")
```

## 原子操作保证

```python
def atomic_save(data: dict, filepath: str):
    """原子保存（要么完全成功，要么完全失败）"""
    
    temp_file = filepath + ".tmp"
    
    try:
        # 1. 写入临时文件
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # 2. 验证 JSON
        with open(temp_file, 'r', encoding='utf-8') as f:
            json.load(f)
        
        # 3. 原子重命名
        os.replace(temp_file, filepath)
        
    except Exception as e:
        # 4. 失败清理
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        raise SaveError(f"保存失败：{e}")
```

## 变更类型

| 类型 | 说明 | 记录内容 |
|------|------|---------|
| `conversation_created` | 创建对话 | 对话名称 |
| `topic_created` | 创建话题 | 话题名称、父话题 ID |
| `topic_switched` | 切换话题 | 原话题 ID、新话题 ID |
| `topic_deleted` | 删除话题 | 话题名称、子话题数 |
| `qa_pair_added` | 添加问答 | 话题 ID、输入预览 |
| `snapshot_saved` | 保存快照 | 快照名称、问答数 |
| `memory_added` | 添加记忆 | 记忆键、类型 |

## 错误处理

```python
class SaveError(Exception):
    """保存错误"""
    pass

async def safe_save(data: dict, filepath: str):
    """安全保存（带重试）"""
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            atomic_save(data, filepath)
            return
        except SaveError as e:
            if attempt == max_retries - 1:
                log.error(f"保存失败（已重试{max_retries}次）: {e}")
                raise
            log.warning(f"保存失败，重试 {attempt + 1}/{max_retries}: {e}")
            await asyncio.sleep(1)  # 等待 1 秒后重试
```

## 协作关系

- 被 **topic-manager** 调用 - 保存话题
- 被 **memory-manager** 调用 - 保存记忆
- 被 **context-navigator** 调用 - 保存快照和状态

## 版本

- **版本**: 1.0.0
- **创建日期**: 2026-03-26
- **维护者**: TalkTree Team
