from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """ 商城智能助手聊天请求 """
    messages: str = Field(
        min_length=1,
        max_length=2000,
        description="用户输入"
    )

    conversation_id: str | None = Field(
        default=None,
        max_length=64,
        description="会话ID，暂时先不传"
    )


class ChatHistoryMessage(BaseModel):
    """ 恢复历史对话 """
    role: Literal["user", "assistant"]
    content: str


class ChatHistoryResponse(BaseModel):
    """指定会话的聊天记录响应。"""

    conversation_id: str
    exists: bool  #用于判断 Redis 中是否存在这个会话
    messages: list[ChatHistoryMessage] = Field(
        default_factory=list
    )


class ChatApprovalDecision(BaseModel):
    """用户对单个危险工具调用的审批决定。"""

    type: Literal["approve", "reject"]

    message: str | None = Field(
        default=None,
        max_length=500,
        description="拒绝原因，批准操作时可以省略",
    )


class ChatResumeRequest(BaseModel):
    """恢复处于 HITL 暂停状态的聊天请求。"""

    conversation_id: str = Field(
        min_length=1,
        max_length=64,
        description="需要恢复的会话 ID"
    )

    interrupt_id: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="approval_required 事件返回的中断 ID",
    )

    decisions: list[ChatApprovalDecision] = Field(
        min_length=1,
        max_length=10,
        description="按照 action_requests 顺序提交的审批决定",
    )