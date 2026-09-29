from app.agents.customer_service import get_customer_service_agent
from app.graph.state import AgentState


async def customer_service_node(state: AgentState):
    """使用当前用户的 MCP 工具处理客服请求。"""
    customer_service_agent = await get_customer_service_agent()

    result = await customer_service_agent.ainvoke(
        {
            "messages": state.messages,
        }
    )

    return {
        "current_agent": "customer",
        "messages": result["messages"],
    }
