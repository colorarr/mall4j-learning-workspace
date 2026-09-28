from app.agents.cart import cart_agent
from app.graph.state import AgentState


def cart_node(state: AgentState):
    result = cart_agent.invoke({
        "messages": state.messages
    })

    return {
        "current_agent": "cart",
        "messages": result["messages"],
    }