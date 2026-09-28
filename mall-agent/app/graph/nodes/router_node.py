#路由
from langchain_core.messages import HumanMessage

from app.core.llm import get_model_with_structured
from app.graph.state import AgentState
from app.schemas.intent import IntentResult

def intent_node(state:AgentState):
    intent_chain = get_model_with_structured(IntentResult)

    result = intent_chain.invoke(
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
