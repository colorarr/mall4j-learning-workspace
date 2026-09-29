from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """ 商城智能助手聊天请求 """
    messages:str = Field(
        min_length=1,
        max_length=2000,
        description="用户输入"
    )

    conversation_id :str | None = Field(
        default=None,
        max_length=64,
        description="会话ID，暂时先不传"
    )