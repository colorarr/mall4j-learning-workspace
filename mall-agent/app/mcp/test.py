import asyncio

from langchain.mcp import MCPAdapter


async def main():
    async with MCPAdapter("http://127.0.0.1:18081/mcp") as mcp:
        tools = await mcp.list_tools()
        print(f"发现 {len(tools)} 个工具")

        tool = next(
            item for item in tools
            if item.name == "product_get_hot_searches"
        )
        result = await tool.ainvoke({"number": 3, "sort": 1})
        print(result)


if __name__ == "__main__":
    asyncio.run(main())