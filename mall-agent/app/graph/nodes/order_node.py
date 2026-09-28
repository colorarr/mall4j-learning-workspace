from app.agents.order import order_agent
from app.graph.state import AgentState


def order_node(state: AgentState):
    result = order_agent.invoke({
        "messages": state.messages
    })

    return {
        "current_agent": "order",
        "messages": result["messages"],
    }
