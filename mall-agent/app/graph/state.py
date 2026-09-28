from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from app.schemas.intent import IntentType


class AgentState(BaseModel):
    user_input: str = Field(
        min_length=1,
        description="用户本轮输入的原始文本",
    )
    messages: Annotated[list[BaseMessage], add_messages] = Field(
        default_factory=list,
        description="当前会话消息，LangGraph 会自动合并新增消息",
    )
    intent: IntentType | None = Field(
        default=None,
        description="路由识别出的用户意图",
    )
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="意图识别置信度，取值范围为 0 到 1",
    )

    intent_reason: str | None = Field(
        default=None,
        description="用一句话说明判断该意图的依据"
    )
    current_agent: str | None = Field(
        default=None,
        description="当前负责处理请求的业务智能体名称",
    )
    response: str | None = Field(
        default=None,
        description="面向用户的最终响应",
    )
