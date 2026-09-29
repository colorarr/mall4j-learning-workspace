from enum import StrEnum


class StreamEventType(StrEnum):
    """前端聊天流支持的事件类型。"""

    # 本次流式请求已经建立，事件中携带 conversation_id。
    START = "start"
    # 当前处理阶段的用户可读状态，例如“正在理解你的问题”。
    STATUS = "status"
    # 意图识别完成，携带意图、置信度和判断原因。
    INTENT = "intent"

    # 已进入具体业务智能体，例如 order、shopping。
    AGENT_START = "agent_start"
    # 业务智能体执行结束，可携带执行状态。
    AGENT_END = "agent_end"

    # 模型已经决定调用某个工具，携带具体工具名称。
    TOOL_CALL = "tool_call"
    # 工具节点开始执行，可能同时执行一个或多个工具。
    TOOL_START = "tool_start"
    # 工具节点执行结束，携带成功或失败状态。
    TOOL_END = "tool_end"

    # 一条面向用户的 AI 消息开始生成。
    MESSAGE_START = "message_start"
    # AI 消息的文本增量，前端应追加到当前消息气泡。
    TOKEN = "token"
    # 当前 AI 消息生成结束，可携带合并后的完整文本。
    MESSAGE_END = "message_end"

    # 长耗时处理期间的保活事件，避免连接被中间层判定为空闲。
    HEARTBEAT = "heartbeat"
    # 整个 Graph 执行完成，携带会话、意图和 Agent 元数据。
    DONE = "done"
    # Graph 或流式传输出现业务异常。
    ERROR = "error"
    # 客户端主动断开或取消了本次流式请求。
    CANCELLED = "cancelled"
