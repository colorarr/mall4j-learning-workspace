from app.agents.customer_service import custom_agent
from app.graph.state import AgentState


def customer_service_node(state: AgentState):
    result = custom_agent.invoke({
        "messages": state.messages
    })

    return {
        "current_agent": "customer",
        "messages": result["messages"],
    }
