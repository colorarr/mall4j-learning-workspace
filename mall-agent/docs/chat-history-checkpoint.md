# LangGraph Redis Checkpoint 聊天记录回显

> 相关文档：中间件、HITL 暂停与恢复执行请阅读
> [`agent-middleware-hitl-resume.md`](./agent-middleware-hitl-resume.md)。

## 1. 文档目标

本文解释商城智能助手如何根据当前登录用户和 `conversation_id`，从 LangGraph Redis Checkpointer 中恢复会话状态，并把适合展示的用户消息和 AI 消息返回给前端。

本文对应的核心接口：

```http
GET /chat/history/{conversation_id}
```

整体流程：

```text
前端 conversation_id
        +
Java 鉴权得到的 user_id
        ↓
生成 LangGraph thread_id
        ↓
graph.aget_state() 读取最新 Checkpoint
        ↓
从 AgentState 中取出 messages
        ↓
保留 HumanMessage 和 AIMessage
        ↓
转换成前端 user/assistant 消息
        ↓
返回 ChatHistoryResponse
```

---

## 2. 为什么使用 thread_id

LangGraph Checkpointer 使用 `thread_id` 区分不同会话。本项目采用以下格式：

```python
thread_id = (
    f"user:{user_context.user_id}"
    f":conversation:{conversation_id}"
)
```

生成结果示例：

```text
user:USER_ID:conversation:CONVERSATION_ID
```

将 `user_id` 放入 `thread_id` 有两个作用：

1. 相同的 `conversation_id` 在不同用户之间仍然相互隔离。
2. 查询历史记录时，服务端根据登录用户重新生成 `thread_id`，前端只负责提供 `conversation_id`。

可以把它理解成：

```text
thread_id = 用户目录 / 会话文件
```

---

## 3. 历史记录响应模型

文件：`app/schemas/chat.py`

```python
from typing import Literal

from pydantic import BaseModel, Field


class ChatHistoryMessage(BaseModel):
    """前端可展示的单条聊天记录。"""

    role: Literal["user", "assistant"]
    content: str


class ChatHistoryResponse(BaseModel):
    """指定会话的聊天记录响应。"""

    conversation_id: str
    exists: bool
    messages: list[ChatHistoryMessage] = Field(
        default_factory=list,
    )
```

### 3.1 ChatHistoryMessage

`ChatHistoryMessage` 是前端真正需要渲染的消息：

| 字段 | 含义 |
|---|---|
| `role` | 消息角色，只允许 `user` 或 `assistant` |
| `content` | 页面上展示的文本 |

工具调用参数、工具原始返回值和系统提示词均不属于该响应模型。

### 3.2 ChatHistoryResponse

| 字段 | 含义 |
|---|---|
| `conversation_id` | 当前查询的会话 ID |
| `exists` | Redis 中是否存在对应会话状态 |
| `messages` | 已经过滤、适合前端渲染的消息列表 |

`default_factory=list` 会为每个响应创建独立列表，避免多个模型实例共享同一个可变默认值。

---

## 4. 历史记录接口

文件：`app/main.py`

推荐实现：

```python
from typing import Annotated

from fastapi import Depends, Path
from langchain_core.messages import AIMessage, HumanMessage

from app.auth.auth_client import UserContext
from app.auth.dependencies import get_user_context
from app.schemas.chat import (
    ChatHistoryMessage,
    ChatHistoryResponse,
)


@app.get(
    "/chat/history/{conversation_id}",
    response_model=ChatHistoryResponse,
)
async def get_chat_history(
        conversation_id: Annotated[
            str,
            Path(
                min_length=1,
                max_length=64,
                pattern=r"^[A-Za-z0-9_-]+$",
            ),
        ],
        user_context: UserContext = Depends(get_user_context),
):
    """读取当前用户指定会话的聊天记录。"""
    thread_id = (
        f"user:{user_context.user_id}"
        f":conversation:{conversation_id}"
    )

    snapshot = await app.state.mall_graph.aget_state(
        {
            "configurable": {
                "thread_id": thread_id,
            }
        }
    )

    values = snapshot.values or {}
    history: list[ChatHistoryMessage] = []

    for message in values.get("messages", []):
        if isinstance(message, HumanMessage):
            role = "user"
        elif isinstance(message, AIMessage):
            role = "assistant"
        else:
            continue

        content = extract_text_content(message.content).strip()
        if not content:
            continue

        if (
            role == "assistant"
            and history
            and history[-1].role == "assistant"
        ):
            history[-1].content += content
            continue

        history.append(
            ChatHistoryMessage(
                role=role,
                content=content,
            )
        )

    return ChatHistoryResponse(
        conversation_id=conversation_id,
        exists=bool(values),
        messages=history,
    )
```

---

## 5. 逐段理解接口

### 5.1 URL 和 response_model

```python
@app.get(
    "/chat/history/{conversation_id}",
    response_model=ChatHistoryResponse,
)
```

前端请求示例：

```http
GET /chat/history/CONVERSATION_ID
```

`response_model` 会让 FastAPI 按照 `ChatHistoryResponse` 校验和序列化返回结果。这里返回的是完整会话对象，因此对应模型是 `ChatHistoryResponse`。

### 5.2 conversation_id 参数校验

```python
conversation_id: Annotated[
    str,
    Path(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]+$",
    ),
]
```

约束如下：

- 长度至少为 1。
- 最大长度为 64。
- 字符范围为字母、数字、下划线和横杠。

这与 `ChatRequest.conversation_id` 的长度约束保持一致。

### 5.3 获取登录用户

```python
user_context: UserContext = Depends(get_user_context)
```

`get_user_context` 的职责：

1. 读取请求头中的 `Authorization`。
2. 调用 Java 内部鉴权接口。
3. 获取商城用户上下文。
4. 将用户上下文注入接口参数。

接口随后通过 `user_context.user_id` 构建用户专属的 `thread_id`。

### 5.4 读取最新 Graph 状态

```python
snapshot = await app.state.mall_graph.aget_state(
    {
        "configurable": {
            "thread_id": thread_id,
        }
    }
)
```

`mall_graph` 在构建时已经接入 Checkpointer：

```python
graph.compile(checkpointer=checkpointer)
```

所以 `aget_state()` 会通过 `thread_id` 从 Checkpointer 读取对应会话的最新状态。业务接口无需直接执行 Redis 查询。

`aget_state()` 返回 `StateSnapshot`，常用属性包括：

| 属性 | 含义 |
|---|---|
| `values` | 最新的 Graph 状态值 |
| `config` | 当前 Checkpoint 配置 |
| `metadata` | Checkpoint 元数据 |
| `next` | 下一批待执行节点 |
| `tasks` | 当前任务信息 |

本接口关注：

```python
snapshot.values
```

### 5.5 values 为什么加 or {}

```python
values = snapshot.values or {}
```

找到会话时，`values` 通常包含：

```python
{
    "user_input": "查询订单",
    "messages": [...],
    "intent": "order_query",
    "current_agent": "order",
}
```

查不到会话时，使用空字典让后续逻辑统一按照空状态处理。

### 5.6 为什么只保留 HumanMessage 和 AIMessage

```python
if isinstance(message, HumanMessage):
    role = "user"
elif isinstance(message, AIMessage):
    role = "assistant"
else:
    continue
```

常见 LangChain 消息类型：

| 消息类型 | 用途 | 前端回显 |
|---|---|---|
| `HumanMessage` | 用户输入 | 保留 |
| `AIMessage` | AI 回复或工具调用决策 | 保留有文本的消息 |
| `ToolMessage` | MCP 工具原始结果 | 跳过 |
| `SystemMessage` | 系统提示词 | 跳过 |

这样前端只展示真正的对话内容。

### 5.7 提取文本

```python
content = extract_text_content(message.content).strip()
if not content:
    continue
```

模型消息内容可能是字符串：

```python
"您的订单已经发货"
```

也可能是标准内容块：

```python
[
    {
        "type": "text",
        "text": "您的订单已经发货",
    }
]
```

`extract_text_content()` 将两种结构统一转换成前端可展示字符串。

工具调用类型的 `AIMessage` 经常只有 `tool_calls`，正文为空。空文本消息会在这里被跳过。

### 5.8 合并连续 AI 消息

Agent 调用工具时，原始消息序列可能是：

```text
HumanMessage
AIMessage       决定调用工具
ToolMessage     工具执行结果
AIMessage       根据工具结果生成最终回答
```

过滤 `ToolMessage` 后，可能得到连续的两个 `assistant` 消息。以下逻辑会把它们合并到同一个前端气泡：

```python
if (
    role == "assistant"
    and history
    and history[-1].role == "assistant"
):
    history[-1].content += content
    continue
```

如果希望两段文本之间明确换行，可以使用：

```python
history[-1].content += "\n\n" + content
```

### 5.9 构建前端消息

```python
history.append(
    ChatHistoryMessage(
        role=role,
        content=content,
    )
)
```

最终消息结构：

```json
{
  "role": "user",
  "content": "查询订单"
}
```

或：

```json
{
  "role": "assistant",
  "content": "您的订单已经发货"
}
```

### 5.10 exists 字段

```python
exists=bool(values)
```

含义：

- `values` 有状态数据：`exists=true`
- `values` 为空：`exists=false`

前端收到 `exists=false` 后，可以清理本地已经失效的 `conversation_id`。

---

## 6. 返回示例

### 6.1 会话存在

```json
{
  "conversation_id": "CONVERSATION_ID",
  "exists": true,
  "messages": [
    {
      "role": "user",
      "content": "查询购物车"
    },
    {
      "role": "assistant",
      "content": "您的购物车中有一件商品"
    }
  ]
}
```

### 6.2 会话为空

```json
{
  "conversation_id": "EMPTY_CONVERSATION_ID",
  "exists": false,
  "messages": []
}
```

---

## 7. 接口测试

### 7.1 测试已有会话

```bash
curl \
  -H "Authorization: TOKEN" \
  "http://127.0.0.1:18082/chat/history/CONVERSATION_ID"
```

检查：

1. HTTP 状态为 `200`。
2. `exists` 为 `true`。
3. `messages` 按对话顺序排列。
4. 消息角色只有 `user` 和 `assistant`。
5. 响应中没有工具原始结果。

### 7.2 测试空会话

```bash
curl \
  -H "Authorization: TOKEN" \
  "http://127.0.0.1:18082/chat/history/EMPTY_CONVERSATION_ID"
```

预期：

```json
{
  "conversation_id": "EMPTY_CONVERSATION_ID",
  "exists": false,
  "messages": []
}
```

### 7.3 测试路径参数

使用超过 64 个字符或包含特殊字符的会话 ID，FastAPI 会返回路径参数校验错误。

---

## 8. 与前端的关系

前端打开聊天窗口时执行以下流程：

```text
读取本地 conversation_id
        ↓
携带 Authorization 请求历史接口
        ↓
exists=true：渲染 messages
exists=false：清理本地 conversation_id
        ↓
滚动到最后一条消息
```

前端无需理解 LangChain 的 `HumanMessage`、`AIMessage` 和 `ToolMessage`，因为后端已经将它们转换为统一结构：

```text
user / assistant / content
```

---

## 9. 常见问题

### 9.1 为什么不用前端直接读取 Redis

Redis Checkpoint 包含 Graph 内部状态、工具结果和模型消息。由后端读取后再转换，可以保持用户隔离，并避免内部数据直接暴露给页面。

### 9.2 aget_state() 返回的是哪一份状态

传入 `thread_id` 且未指定 `checkpoint_id` 时，LangGraph 返回该线程的最新状态。它适合恢复当前会话。

### 9.3 这是完整的 Checkpoint 时间线吗

本接口读取的是最新状态中的 `messages`。如果后续需要查看每一次 Graph 执行产生的 Checkpoint 时间线，可以研究：

```python
graph.aget_state_history(config)
```

聊天记录回显通常使用最新状态已经足够。

### 9.4 为什么会出现多个 AIMessage

ReAct Agent 可能先生成工具调用消息，等待工具结果后再生成最终回答。一次用户请求对应多个内部 AI 消息属于正常现象。

### 9.5 为什么查到的 messages 为空

重点检查：

1. 前端提交的 `conversation_id` 是否与聊天请求使用的值一致。
2. 当前登录用户是否与创建会话的用户一致。
3. `thread_id` 的拼接规则是否完全一致。
4. Graph 是否使用同一个 Redis Checkpointer。
5. Redis 数据是否仍然存在。

---

## 10. 后续扩展

当前接口解决的是“根据已知 conversation_id 恢复一个会话”。后续可以继续扩展：

1. 会话列表：列出当前用户的多个会话。
2. 会话标题：使用第一条用户消息或模型摘要生成标题。
3. 更新时间：按最近对话时间排序。
4. 历史分页：长会话分批加载。
5. 会话删除：同时清理会话元数据和 Checkpoint。
6. 会话重命名：允许用户修改标题。
7. 长会话压缩：对早期内容生成摘要，控制模型上下文长度。

实现会话列表时，推荐单独维护会话元数据，例如：

```text
conversation_id
user_id
title
created_at
updated_at
```

Checkpoint 继续负责 Graph 状态，会话元数据负责列表查询、排序、标题和生命周期管理。
