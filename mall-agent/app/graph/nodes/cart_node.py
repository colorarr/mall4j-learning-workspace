from app.agents.cart import get_cart_agent
from app.graph.state import AgentState


async def cart_node(state: AgentState):
    """使用当前用户的 MCP 工具处理购物车请求。"""
    cart_agent = await get_cart_agent()

    result = await cart_agent.ainvoke(
        {
            "messages": state.messages,
        }
    )

    return {
        "current_agent": "cart",
        "messages": result["messages"],
    }
