import asyncio

from langchain_core.tools import tool

from app.rag.retriever import search_knowledge

@tool
async def search_customer_knowledge(query:str)->dict:
    """检索商城客服知识库。

    用于配送、运费、支付、优惠券、订单规则、
    退款退货流程和收货地址管理等通用问题。

    query 应是明确的商城问题。
    此工具不查询实时订单、物流、价格或退款进度。
    """

    # 当前检索使用同步客户端，放在线程中执行，
    # 避免阻塞 FastAPI 的异步事件循环。

    results = await asyncio.to_thread(
        search_knowledge,
        query
    )

    documents = [
        {
            "title":document.metadata.get("title",""),
            "source":document.metadata.get("source",""),
            "chunk_id":document.metadata.get("chunk_id",""),
            "score":round(float(score),4),
            "content":document.page_content,
        }
        for document,score in results
    ]

    return {
        "query":query,
        "documents":documents,
        "note": (
            "检索结果是候选资料，分数不是回答置信度。"
            "仅使用与问题直接相关的内容；"
            "资料未说明的政策、金额和时效不得推断。"
        ),
    }

if __name__ == "__main__":
    import json

    async def main() -> None:
        result = await search_customer_knowledge.ainvoke(
            {
                "query": "优惠券为什么在结算时用不了？",
            }
        )

        print(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
            )
        )

    asyncio.run(main())