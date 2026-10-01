from uuid import uuid5, NAMESPACE_URL

from qdrant_client.http.models import VectorParams, Distance

from app.core.config import Settings, settings
from app.core.embeddings import get_embedding_model
from app.rag.loader import load_knowledge_documents
from app.rag.splitter import split_knowledge_documents
from app.rag.vector_store import get_qdrant_client, get_qdrant_vector_store


def ingest_knowledge():
    """加载知识文档、切片，并写入 Qdrant。"""

    #1.加载文档
    documents = load_knowledge_documents()

    if not documents:
        raise ValueError("加载的文档为空")
    #2.切片
    chunks = split_knowledge_documents(documents)
    if not chunks:
        raise ValueError("文档切分结果为空")

    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION

    # 3. 首次导入时，创建向量集合
    if not client.collection_exists(collection_name):
        embedding_model = get_embedding_model()

        # 向量维度由实际使用的 Embedding 模型决定
        sample_vector = embedding_model.embed_query(
            "知识库向量维度检测"
        )
        vector_size = len(sample_vector)

        print("向量维度:", vector_size)

        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )

        print("已创建集合:", collection_name)
    else:
        print("使用已有集合:", collection_name)

    # 4. 为每个 Chunk 生成稳定的 Qdrant Point ID
    point_ids: list[str] = []

    for chunk in chunks:
        if not chunk.id:
            raise ValueError("Chunk 缺少 ID，请检查 splitter")

        # 保留可读的业务 ID，方便查看来源和排查问题
        chunk.metadata["chunk_id"] = chunk.id

        # Qdrant Point ID 使用 UUID
        point_id = str(
            uuid5(
                NAMESPACE_URL,
                f"mall-knowledge:{chunk.id}",
            )
        )

        point_ids.append(point_id)

        # 5. VectorStore 自动调用 Embedding 模型并写入 Qdrant
    vector_store = get_qdrant_vector_store()

    written_ids = vector_store.add_documents(
        documents=chunks,
        ids=point_ids,
        batch_size=16,
        wait=True,
    )

    print("本次写入数量:", len(written_ids))

    # 6. 查询集合中的实际 Point 数量
    result = client.count(
        collection_name=collection_name,
        exact=True,
    )

    print("集合 Point 总数:", result.count)
    print("知识库导入完成")


if __name__ == "__main__":
    ingest_knowledge()