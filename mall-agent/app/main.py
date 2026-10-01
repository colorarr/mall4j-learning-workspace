import asyncio
import json
import logging
import uuid
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command
from starlette import status

from app.auth.auth_client import UserContext
from app.auth.dependencies import get_user_context
from app.graph.main_graph import build_graph
from app.memory.checkpointer import checkpointer
from app.schemas.chat import ChatRequest, ChatHistoryMessage, ChatHistoryResponse, ChatResumeRequest
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
    async with checkpointer as saver:
        app.state.mall_graph = build_graph(saver)
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

    result = await app.state.mall_graph.ainvoke({
        'user_input': request.messages,
        'messages': [],
    },
        config={
            "configurable": {
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
            async for part in app.state.mall_graph.astream(
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
                    interrupts = data.get("__interrupt__")

                    if interrupts:
                        current_interrupt = interrupts[0]
                        interrupt_id = getattr(
                            current_interrupt,
                            "id",
                            None,
                        )
                        interrupt_value = getattr(
                            current_interrupt,
                            "value",
                            {},
                        )

                        if not isinstance(interrupt_value, dict):
                            interrupt_value = {}

                        yield encode_stream_event(
                            StreamEventType.APPROVAL_REQUIRED,
                            conversation_id=conversation_id,
                            interrupt_id=interrupt_id,
                            actions=interrupt_value.get(
                                "action_requests",
                                [],
                            ),
                            review_configs=interrupt_value.get(
                                "review_configs",
                                [],
                            ),
                        )

                        # Graph 此时处于暂停状态。审批完成后由恢复接口
                        # 使用相同 conversation_id 继续执行。
                        return

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


@app.get("/chat/history/{conversation_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
        conversation_id: str,
        user_context: UserContext = Depends(get_user_context)
        ):
    """ 读取当前用户指定会话的聊天记录。 """
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


@app.post("/chat/resume")
async def resume_chat(
        request: ChatResumeRequest,
        user_context: UserContext = Depends(
            get_user_context,
            scope="request",
        ),
):
    """校验并恢复处于 HITL 暂停状态的会话。"""
    thread_id = (
        f"user:{user_context.user_id}"
        f":conversation:{request.conversation_id}"
    )

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    snapshot = await app.state.mall_graph.aget_state(config)

    pending_interrupts = [
        pending_interrupt
        for task in snapshot.tasks
        for pending_interrupt in task.interrupts
    ]

    if not pending_interrupts:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="当前会话没有待审批操作",
        )

    current_interrupt = next(
        (
            pending_interrupt
            for pending_interrupt in pending_interrupts
            if pending_interrupt.id == request.interrupt_id
        ),
        None,
    )

    if current_interrupt is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="审批请求已经失效或中断 ID 不匹配",
        )

    interrupt_value = current_interrupt.value

    if not isinstance(interrupt_value, dict):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="审批状态数据格式异常",
        )

    action_requests = interrupt_value.get(
        "action_requests",
        [],
    )
    review_configs = interrupt_value.get(
        "review_configs",
        [],
    )

    if len(request.decisions) != len(action_requests):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="审批决定数量与待审批操作数量不一致",
        )

    if len(review_configs) != len(action_requests):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="待审批操作配置不完整",
        )

    for decision, review_config in zip(
            request.decisions,
            review_configs,
            strict=True,
    ):
        allowed_decisions = review_config.get(
            "allowed_decisions",
            [],
        )

        if decision.type not in allowed_decisions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"当前操作不支持审批决定："
                    f"{decision.type}"
                ),
            )

    decisions = [
        decision.model_dump(exclude_none=True)
        for decision in request.decisions
    ]
    approved_tool_names = [
        action.get("name")
        for action, decision in zip(
            action_requests,
            request.decisions,
            strict=True,
        )
        if decision.type == "approve"
        and isinstance(action, dict)
        and action.get("name")
    ]

    values = snapshot.values or {}
    intent_value = values.get("intent")
    intent = getattr(intent_value, "value", intent_value)
    initial_agent = snapshot.next[0] if snapshot.next else None

    async def generate():
        current_agent = initial_agent
        full_content = ""
        message_started = False
        active_tool_names = approved_tool_names.copy()

        yield encode_stream_event(
            StreamEventType.START,
            conversation_id=request.conversation_id,
            resumed=True,
            interrupt_id=request.interrupt_id,
        )
        yield encode_stream_event(
            StreamEventType.STATUS,
            stage="approval",
            message=(
                "审批已通过，正在执行操作"
                if approved_tool_names
                else "操作已拒绝，正在生成回复"
            ),
        )

        try:
            async for part in app.state.mall_graph.astream(
                    Command(
                        resume={
                            "decisions": decisions,
                        }
                    ),
                    config=config,
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

                    if metadata.get("langgraph_node") != "model":
                        continue

                    for tool_chunk in (
                            getattr(
                                message_chunk,
                                "tool_call_chunks",
                                None,
                            ) or []
                    ):
                        tool_name = tool_chunk.get("name")
                        if (
                                tool_name
                                and tool_name not in active_tool_names
                        ):
                            active_tool_names.append(tool_name)
                            yield encode_stream_event(
                                StreamEventType.TOOL_CALL,
                                name=tool_name,
                            )

                    content = extract_text_content(
                        message_chunk.content
                    )
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
                    interrupts = data.get("__interrupt__")

                    if interrupts:
                        next_interrupt = interrupts[0]
                        next_interrupt_value = getattr(
                            next_interrupt,
                            "value",
                            {},
                        )
                        if not isinstance(next_interrupt_value, dict):
                            next_interrupt_value = {}

                        yield encode_stream_event(
                            StreamEventType.APPROVAL_REQUIRED,
                            conversation_id=request.conversation_id,
                            interrupt_id=getattr(
                                next_interrupt,
                                "id",
                                None,
                            ),
                            actions=next_interrupt_value.get(
                                "action_requests",
                                [],
                            ),
                            review_configs=next_interrupt_value.get(
                                "review_configs",
                                [],
                            ),
                        )
                        return

                elif stream_type == "tasks":
                    task_name = data.get("name")
                    task_finished = (
                        "result" in data or "error" in data
                    )

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
                conversation_id=request.conversation_id,
                intent=intent,
                agent=current_agent,
            )

        except asyncio.CancelledError:
            logger.info(
                "Chat resume stream cancelled: %s",
                request.conversation_id,
            )
            raise
        except Exception:
            logger.exception(
                "Chat resume stream failed: %s",
                request.conversation_id,
            )
            yield encode_stream_event(
                StreamEventType.ERROR,
                message="智能助手恢复执行失败，请稍后重试",
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
