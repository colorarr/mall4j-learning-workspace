from qdrant_client import QdrantClient

from app.core.config import settings


def main() -> None:
    client = QdrantClient(
        url=settings.QDRANT_BASE_URL,
        api_key=settings.QDRANT_API_KEY,
        timeout=20,
    )

    response = client.get_collections()

    print("Qdrant Cloud 连接成功")
    print("当前集合：")

    if not response.collections:
        print("- 暂无集合")
        return

    for collection in response.collections:
        print("-", collection.name)


if __name__ == "__main__":
    main()