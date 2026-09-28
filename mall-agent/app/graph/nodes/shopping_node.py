from app.agents.shopping import shopping_agent
from app.graph.state import AgentState


def shopping_node(state: AgentState):
    result = shopping_agent.invoke({
        "messages": state.messages
    })

    return {
        "current_agent": "shopping",
        "messages": result["messages"],
    }
