from functools import lru_cache

from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore

from app.core.config import settings
from app.rag.vector_store import get_qdrant_vector_store


@lru_cache(maxsize=1)
def get_knowledge_vector_store() -> QdrantVectorStore:
    """缓存知识库 VectorStore，复用客户端和 Embedding 模型。"""

    return get_qdrant_vector_store()


def search_knowledge(
        query:str,
        top_k:int | None = None,
)->list[tuple[Document, float]]:
    query = query.strip()

    if not query:
        raise ValueError("检索问题为空")

    k = settings.RAG_TOP_K if top_k is None else top_k

    if k < 1:
        raise ValueError("top_k 必须大于 0")

    vector_store = get_knowledge_vector_store()

    return vector_store.similarity_search_with_score(
        query=query,
        k=k,
    )

if __name__ == "__main__":
    query = "优惠券为什么在结算时用不了？"

    results = search_knowledge(
        query=query,
        top_k=3,
    )

    print("检索问题:", query)
    print("命中数量:", len(results))

    for index, (document, score) in enumerate(
        results,
        start=1,
    ):
        print("=" * 60)
        print("排名:", index)
        print("相似度:", round(score, 4))
        print("标题:", document.metadata.get("title"))
        print("分类:", document.metadata.get("category"))
        print("来源:", document.metadata.get("source_path"))
        print("Chunk ID:", document.metadata.get("chunk_id"))
        print("正文:")
        print(document.page_content)