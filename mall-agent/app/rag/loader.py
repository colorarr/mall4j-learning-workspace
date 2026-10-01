from pathlib import Path

from langchain_core.documents import Document

KNOWLEDGE_DIR = Path(__file__).resolve().parents[2] / "knowledge"


def load_knowledge_documents() -> list[Document]:
    """加载 knowledge 分类目录中的全部 Markdown 文档。"""

    documents: list[Document] = []

    # 获取指定规则下的文件，列表中的元素都是 Path 对象
    markdown_files = sorted(KNOWLEDGE_DIR.glob("*/*.md"))

    for markdown_file in markdown_files:
        # 文档正文
        content = markdown_file.read_text(encoding="utf-8").strip()

        # 相对于 knowledge 目录的文件路径
        relative_path = markdown_file.relative_to(
            KNOWLEDGE_DIR,
        )

        # 文件名作为标题
        title = markdown_file.stem

        # 父目录名作为分类
        category = markdown_file.parent.name

        # 暂时使用相对路径作为稳定 ID
        document_id = relative_path.with_suffix("").as_posix()



        # 构建原始 Document 对象
        document = Document(
            id=document_id,
            page_content=content,
            metadata={
                "document_id": document_id,
                "title": title,
                "category": category,
                "source_path": relative_path.as_posix(),
            },
        )

        documents.append(document)

    return documents


if __name__ == "__main__":
    documents = load_knowledge_documents()

    print("原始文档数量:", len(documents))

    for document in documents:
        print("=" * 60)
        print("Document ID:", document.id)
        print("标题:", document.metadata["title"])
        print("分类:", document.metadata["category"])
        print("来源:", document.metadata["source_path"])
        print("长度:", len(document.page_content))
