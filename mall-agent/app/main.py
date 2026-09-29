import asyncio
import json
import logging
import uuid
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse

from app.auth.auth_client import UserContext
from app.auth.dependencies import get_user_context
from app.graph.main_graph import mall_graph
from app.memory.redis import redis_checkpointer
from app.schemas.chat import ChatRequest
from app.schemas.stream import StreamEventType


logger = logging.getLogger(__name__)

AGENT_NODES = {
    "shopping",
    "cart",
    "customer",
    "order",
}


def encode_stream_event(
        event_type: StreamEventType,
        **payload: Any,
) -> bytes:
    """将业务流事件编码为标准 SSE 帧。"""
    data = json.dumps(
        payload,
        ensure_ascii=False,
        default=str,
    )
    return (
        f"event: {event_type.value}\n"
        f"data: {data}\n\n"
    ).encode("utf-8")


def extract_text_content(content: Any) -> str:
    """兼容字符串和标准文本内容块，只提取可展示文本。"""
    if isinstance(content, str):
        return content

    if not isinstance(content, list):
        return ""

    text_parts: list[str] = []
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "text" and isinstance(block.get("text"), str):
            text_parts.append(block["text"])

    return "".join(text_parts)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with redis_checkpointer:
        yield


app = FastAPI(
    title="Mall Agent Api",
    description="Mall Agent API",
    version="1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/chat")
async def auth_check(
        user_context: UserContext = Depends(get_user_context),
):
    return {
        "userId": user_context.user_id,
        "shopId": user_context.shop_id,
        "sysType": user_context.sys_type,
        "isAdmin": user_context.is_admin,
        "enabled": user_context.enabled,
        "perms": sorted(user_context.perms),
    }


@app.post("/chat")
async def chat(
        request: ChatRequest,
        user_context: UserContext = Depends(get_user_context), ):

    conversation_id = request.conversation_id or uuid.uuid4().hex

    thread_id = (
        f"user:{user_context.user_id}"
        f":conversation:{conversation_id}"
    )

    result = await mall_graph.ainvoke({
        'user_input': request.messages,
        'messages': [],
    },
    config={
        "configurable":{
            "thread_id": thread_id,
        }
    }
    )
    return {
        "conversation_id": conversation_id,
        "reply": result["messages"][-1].content,
        "intent": result["intent"],
        "agent": result["current_agent"],
    }


@app.post("/chat/stream")
async def chat_stream(
        request: ChatRequest,
        user_context: UserContext = Depends(
            get_user_context,
            scope="request",
        ),
):
    conversation_id = request.conversation_id or uuid.uuid4().hex
    thread_id = (
        f"user:{user_context.user_id}"
        f":conversation:{conversation_id}"
    )

    async def generate():
        intent: str | None = None
        current_agent: str | None = None
        full_content = ""
        message_started = False
        active_tool_names: list[str] = []

        yield encode_stream_event(
            StreamEventType.START,
            conversation_id=conversation_id,
        )
        yield encode_stream_event(
            StreamEventType.STATUS,
            stage="intent",
            message="正在理解你的问题",
        )

        try:
            async for part in mall_graph.astream(
                    {
                        "user_input": request.messages,
                        "messages": [],
                    },
                    config={
                        "configurable": {
                            "thread_id": thread_id,
                        }
                    },
                    stream_mode=[
                        "messages",
                        "updates",
                        "tasks",
                    ],
                    subgraphs=True,
                    version="v2",
            ):
                stream_type = part["type"]
                namespace = part["ns"]
                data = part["data"]

                if stream_type == "messages":
                    message_chunk, metadata = data

                    # intent 是内部结构化输出，tools 是工具原始结果；只处理
                    # 业务 Agent 的 model 节点，避免把 IntentResult 等内部调用
                    # 当作商城工具事件发送给前端。
                    if metadata.get("langgraph_node") != "model":
                        continue

                    for tool_chunk in (
                            getattr(message_chunk, "tool_call_chunks", None) or []
                    ):
                        tool_name = tool_chunk.get("name")
                        if tool_name and tool_name not in active_tool_names:
                            active_tool_names.append(tool_name)
                            yield encode_stream_event(
                                StreamEventType.TOOL_CALL,
                                name=tool_name,
                            )

                    content = extract_text_content(message_chunk.content)
                    if not content:
                        continue

                    if not message_started:
                        message_started = True
                        yield encode_stream_event(
                            StreamEventType.MESSAGE_START,
                        )

                    full_content += content
                    yield encode_stream_event(
                        StreamEventType.TOKEN,
                        content=content,
                    )

                elif stream_type == "updates" and not namespace:
                    intent_update = data.get("intent")
                    if not isinstance(intent_update, dict):
                        continue

                    intent_value = intent_update.get("intent")
                    intent = getattr(intent_value, "value", intent_value)
                    yield encode_stream_event(
                        StreamEventType.INTENT,
                        intent=intent,
                        confidence=intent_update.get("confidence"),
                        reason=intent_update.get("intent_reason"),
                    )

                elif stream_type == "tasks":
                    task_name = data.get("name")
                    task_finished = "result" in data or "error" in data

                    if not namespace and task_name in AGENT_NODES:
                        current_agent = task_name
                        event_type = (
                            StreamEventType.AGENT_END
                            if task_finished
                            else StreamEventType.AGENT_START
                        )
                        yield encode_stream_event(
                            event_type,
                            agent=task_name,
                            success=(data.get("error") is None)
                            if task_finished
                            else None,
                        )

                    elif namespace and task_name == "tools":
                        event_type = (
                            StreamEventType.TOOL_END
                            if task_finished
                            else StreamEventType.TOOL_START
                        )
                        yield encode_stream_event(
                            event_type,
                            names=active_tool_names.copy(),
                            success=(data.get("error") is None)
                            if task_finished
                            else None,
                        )

                        if task_finished:
                            active_tool_names.clear()

            if message_started:
                yield encode_stream_event(
                    StreamEventType.MESSAGE_END,
                    content=full_content,
                )

            yield encode_stream_event(
                StreamEventType.DONE,
                conversation_id=conversation_id,
                intent=intent,
                agent=current_agent,
            )

        except asyncio.CancelledError:
            logger.info(
                "Chat stream cancelled: %s",
                conversation_id,
            )
            raise
        except Exception:
            logger.exception(
                "Chat stream failed: %s",
                conversation_id,
            )
            yield encode_stream_event(
                StreamEventType.ERROR,
                message="智能助手执行失败，请稍后重试",
            )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "X-Content-Type-Options": "nosniff",
        },
    )
