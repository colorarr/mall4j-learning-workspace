from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


# 定义适合中文知识文档的文本切割器
knowledge_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    separators=[
        "\n\n",
        "\n",
        "。",
        "！",
        "？",
        "；",
        "，",
        " ",
        "",
    ],
)


def split_knowledge_documents(
    documents: list[Document],
) -> list[Document]:
    """把原始知识文档切分成适合向量检索的 Chunk。"""

    chunks = knowledge_text_splitter.split_documents(
        documents,
    )

    document_chunk_counters: dict[str, int] = {}

    for chunk in chunks:
        document_id = chunk.metadata["document_id"]

        chunk_index = document_chunk_counters.get(
            document_id,
            0,
        )

        chunk.id = f"{document_id}:chunk:{chunk_index}"
        chunk.metadata["chunk_index"] = chunk_index

        document_chunk_counters[document_id] = (
            chunk_index + 1
        )

    return chunks


if __name__ == "__main__":
    from app.rag.loader import load_knowledge_documents

    documents = load_knowledge_documents()
    chunks = split_knowledge_documents(documents)

    print("原始文档数量:", len(documents))
    print("Chunk 数量:", len(chunks))

    for chunk in chunks:
        print("=" * 60)
        print("Chunk ID:", chunk.id)
        print("标题:", chunk.metadata["title"])
        print("分类:", chunk.metadata["category"])
        print("来源:", chunk.metadata["source_path"])
        print("序号:", chunk.metadata["chunk_index"])
        print("长度:", len(chunk.page_content))
