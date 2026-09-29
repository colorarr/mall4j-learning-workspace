import asyncio

from app.core.config import settings
from app.mcp.client import load_mcp_tools, select_tools


async def main():
    authorization = settings.TEST_MALL_TOKEN

    if not authorization:
        raise RuntimeError("请先设置 TEST_MALL_TOKEN")

    tools = await load_mcp_tools(authorization)
    order_tools = select_tools(tools, "order_")

    print(f"全部工具：{len(tools)}")
    print(f"订单工具：{len(order_tools)}")
    print([tool.name for tool in order_tools])

    order_counts_tool = next(
        tool
        for tool in order_tools
        if tool.name == "order_get_counts"
    )

    result = await order_counts_tool.ainvoke({})
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
