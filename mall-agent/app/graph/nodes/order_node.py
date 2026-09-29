from app.agents.order import get_order_agent
from app.graph.state import AgentState


async def order_node(state: AgentState):
    order_agent = await get_order_agent()

    result = await order_agent.ainvoke({
        "messages":state.messages
    })

    return {
        "current_agent": "order",
        "messages": result["messages"],
    }
