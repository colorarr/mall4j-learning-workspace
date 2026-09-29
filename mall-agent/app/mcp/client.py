from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from app.auth.request_context import get_authorization
from app.core.config import settings


def create_mcp_client(
        authorization: str
) -> MultiServerMCPClient:
    """ 创建携带当前商城用户 Token 的 MCP Client。 """
    if not authorization:
        raise ValueError("非法用户禁止访问")

    return MultiServerMCPClient({
        "mall": {
            "transport": "streamable_http",
            "url": settings.MCP_SERVER_URL,
            "headers": {
                "Authorization": authorization,
            }
        }
    })


async def load_mcp_tools(
        authorization: str
) -> list[BaseTool]:
    """ 加载mcp的工具集 """
    client = create_mcp_client(authorization)
    return await client.get_tools(server_name="mall")


def select_tools(
        tools: list[BaseTool],
        *prefix: str
) -> list[BaseTool]:
    """按照工具名称前缀筛选业务智能体所需工具。"""
    prefix_tools = []
    for tool in tools:
        if tool.name.startswith(prefix):
            prefix_tools.append(tool)
    return prefix_tools


async def load_current_user_tools(
    *prefixes: str,
) -> list[BaseTool]:
    """加载当前请求用户指定分组的 MCP 工具。"""
    authorization = get_authorization()
    tools = await load_mcp_tools(authorization)
    return select_tools(tools, *prefixes)