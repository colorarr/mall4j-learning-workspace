from functools import lru_cache

from langchain_qdrant import QdrantVectorStore, RetrievalMode
from qdrant_client import QdrantClient

from app.core.config import settings
from app.core.embeddings import get_embedding_model


@lru_cache(maxsize=1)
def get_qdrant_client():
    """创建并缓存 Qdrant Cloud 客户端。"""
    client = QdrantClient(
        url=settings.QDRANT_BASE_URL,
        api_key=settings.QDRANT_API_KEY,
        timeout=20,
    )

    return client

def get_qdrant_vector_store():
    """获取已经完成初始化的知识库向量存储。"""

    return QdrantVectorStore(
        client=get_qdrant_client(),
        collection_name=settings.QDRANT_COLLECTION,
        embedding=get_embedding_model(),
        retrieval_mode=RetrievalMode.DENSE
    )

if __name__ == "__main__":
    client = get_qdrant_client()

    response = client.get_collections()

    print("Qdrant Client 初始化成功")
    print(
        "目标集合：",
        settings.QDRANT_COLLECTION,
    )
    print(
        "目标集合是否存在：",
        client.collection_exists(
            settings.QDRANT_COLLECTION,
        ),
    )

    print(
        "现有集合：",
        [
            collection.name
            for collection in response.collections
        ],
    )