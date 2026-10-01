#路由
from langchain_core.messages import HumanMessage

from app.core.llm import get_model_with_structured
from app.graph.state import AgentState
from app.schemas.intent import IntentResult

async def intent_node(state:AgentState):
    # 结构化模型统一关闭深度思考，减少分类等待。
    intent_chain = get_model_with_structured(IntentResult)

    result = await intent_chain.ainvoke(
        {
            "input":state.user_input
        }
    )


    return {
        "intent": result.intent,
        "confidence": result.confidence,
        "intent_reason": result.intent_reason,
        "messages": [HumanMessage(content=state.user_input)],
    }
