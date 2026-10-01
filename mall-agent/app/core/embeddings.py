from langchain_openai import OpenAIEmbeddings

from app.core.config import settings


def get_embedding_model():
    return OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        base_url=settings.EMBEDDING_BASE_URL,
        api_key=settings.EMBEDDING_API_KEY,
        # embedding-3 不是 OpenAI 官方模型名，
        # 跳过 tiktoken 的模型名称检查
        check_embedding_ctx_length=False,
    )


if __name__ == "__main__":
    embedding_model = get_embedding_model()

    vector = embedding_model.embed_query(
        "退款一般需要多久到账？"
    )

    print("向量类型:", type(vector))
    print("向量维度:", len(vector))
    print("前 5 个数值:", vector[:5])