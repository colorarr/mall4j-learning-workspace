from app.agents.shopping import get_shopping_agent
from app.graph.state import AgentState


async def shopping_node(state: AgentState):
    """使用商品 MCP 工具处理导购请求。"""
    shopping_agent = await get_shopping_agent()

    result = await shopping_agent.ainvoke(
        {
            "messages": state.messages,
        }
    )

    return {
        "current_agent": "shopping",
        "messages": result["messages"],
    }