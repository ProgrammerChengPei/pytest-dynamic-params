***

name: "conversation"
description: "管理对话流程和状态转换。在处理任务、话题、问答交互时调用。"
--------------------------------------------

# 对话管理规则

## 核心概念

### Task（任务）

用户发起的完整工作单元，具有独立的生命周期。

| 状态            | 说明       |
| ------------- | -------- |
| **IDLE**      | 空闲/无活动任务 |
| **ACTIVE**    | 进行中      |
| **PAUSED**    | 已暂停（可恢复） |
| **COMPLETED** | 已完成      |
| **ABANDONED** | 已放弃      |

### Topic（话题）

Task 内的一个主题单元，一个 Task 可包含多个 Topic。

| 状态            | 说明           |
| ------------- | ------------ |
| **ACTIVE**    | 当前活跃话题       |
| **PAUSED**    | 已暂停（切换到其他话题） |
| **COMPLETED** | 已完成          |
| **ABANDONED** | 已放弃          |

### QA（问答）

Topic 内的一次完整问答交互。

| 状态              | 说明        |
| --------------- | --------- |
| **PROCESSING**  | AI 正在处理   |
| **WAITING**     | 等待用户确认/输入 |
| **COMPLETED**   | 已完成       |
| **INTERRUPTED** | 已中断（可恢复）  |

***

## 状态记录文件

所有对话状态记录在 `.trae/status/conversation.yaml` 文件中，包含：

- Task 列表及其状态
- 每个 Task 包含的 Topic 列表
- 每个 Topic 包含的 QA 列表
- 每个对象的唯一 ID、创建时间、更新时间等信息

### 唯一 ID 生成规则

- **Task ID**: `T-{timestamp}-{random4}` (例：`T-20260326192600-a1b2`)
- **Topic ID**: `TP-{task_id}-{sequence}` (例：`TP-T-20260326192600-a1b2-001`)
- **QA ID**: `QA-{topic_id}-{sequence}` (例：`QA-TP-T-20260326192600-a1b2-001-001`)

***

## 用户指令集

### Task 级别指令

| 指令                              | 说明         | 触发条件         |
| ------------------------------- | ---------- | ------------ |
| `/continue [task_id/task_name]` | 继续指定任务     | IDLE, PAUSED |
| `/merge [task_id/task_name]`    | 继承指定任务的上下文 | IDLE         |
| `/status [task_id/task_name]`   | 查看任务状态     | 任意           |
| `/save [task_id/task_name]`     | 保存进度，存储记忆  | PAUSED       |

### Topic 级别指令

| 指令                               | 说明               | 触发条件           |
| -------------------------------- | ---------------- | -------------- |
| `/new [topic_name]`              | 新建话题，名称可由用户输入或为空 | IDLE           |
| `/status [topic_id/topic_desc]`  | 查看话题状态           | 任意             |
| `/save [topic_id/topic_desc]`    | 保存进度，存储记忆        | PAUSED         |
| `/abandon [topic_id/topic_desc]` | 放弃当前话题           | ACTIVE, PAUSED |

### QA 级别指令

| 指令          | 说明              | 触发条件                    |
| ----------- | --------------- | ----------------------- |
| `/stop`     | 停止当前问答（UI 停止按钮） | PROCESSING              |
| `/continue` | 继续执行            | INTERRUPTED             |
| `/abandon`  | 放弃当前问答的执行结果     | INTERRUPTED 或 COMPLETED |
| `/adjust`   | 调整方案后继续         | WAITING                 |

***

## 状态管理规则

### Task 状态转换

- `IDLE` → `ACTIVE`: 用户通过 UI 创建新任务
- `ACTIVE` → `PAUSED`: 用户暂停任务
- `ACTIVE` → `COMPLETED`: 所有话题完成
- `ACTIVE` → `ABANDONED`: 用户放弃任务
- `PAUSED` → `ACTIVE`: 用户继续任务
- `PAUSED` → `COMPLETED`: 用户确认完成
- `PAUSED` → `ABANDONED`: 用户放弃任务

### Topic 状态转换

- `IDLE` → `ACTIVE`: 用户创建新话题（`/new`）
- `ACTIVE` → `PAUSED`: 切换到其他话题
- `ACTIVE` → `COMPLETED`: 话题内所有 QA 完成
- `ACTIVE` → `ABANDONED`: 用户放弃话题（`/abandon`）
- `PAUSED` → `ACTIVE`: 切换回该话题
- `PAUSED` → `COMPLETED`: 用户确认完成
- `PAUSED` → `ABANDONED`: 用户放弃话题

### QA 状态转换

- `IDLE` → `PROCESSING`: 用户输入，AI 开始处理
- `PROCESSING` → `WAITING`: AI 处理完成，等待确认
- `PROCESSING` → `INTERRUPTED`: 用户点击停止（`/stop`）
- `WAITING` → `PROCESSING`: 用户调整方案（`/adjust`）
- `WAITING` → `COMPLETED`: 用户确认
- `INTERRUPTED` → `PROCESSING`: 用户继续（`/continue`）
- `INTERRUPTED` → `COMPLETED`: 用户放弃执行结果（`/abandon`）

***

## 话题切换与跨任务处理

### 场景一：同一任务内切换话题

**处理规则：**

1. **明确切换**（用户主动说明）
   - 当用户明确表示切换话题时（如"换个话题"）
   - 当前 Topic 进入 PAUSED
   - 创建新 Topic 或切换到已存在的话题
2. **隐式切换**（上下文自然转移）
   - 当用户问题与当前上下文明显无关时
   - 提醒用户确认是否开启新话题
   - 用户确认后创建新 Topic

### 场景二：跨任务联系

**处理规则：**

1. **任务 ID/名称引用**
   - 用户可通过任务 ID 或名称引用其他任务
   - AI 主动询问是否需要加载引用任务的上下文
2. **上下文继承**
   - 用户可以要求继承上一个任务的上下文（`/merge`）
   - AI 确认继承内容后继续
3. **项目级记忆**
   - 将用户偏好、项目背景存储到 `.trae/status/conversation.yaml`
   - 新任务自动加载项目上下文

***

## 默认采纳机制

- 对话中如果用户对 AI 的回答没有提出质疑，**默认就是采纳**
- 采纳意味着用户认可 AI 的回答内容，不需要进一步修改或澄清
- AI 可以继续推进任务，无需反复确认

***

## 质疑与修改流程

- 用户可能会对 AI 回答的某个点产生质疑，逐步修改 AI 的回答
- 每次质疑都是对回答的**局部调整**，而非整体否定
- AI 应根据质疑内容调整方案，而非重新开始

***

## 执行前汇总原则

- 当用户明确表示**开始执行**时，AI 需要汇总几次质疑的最终结果
- 按**最终汇总结果**去执行，确保执行方案是所有讨论和修改的综合结果

