from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"

if __name__ == "__main__":
    print(ENV_PATH)


class Settings(BaseSettings):
    MODEL_NAME: str
    BASE_URL: str
    API_KEY: str
    TAVILY_API_KEY:str
    JAVA_AUTH_INTROSPECT_URL: str = "http://127.0.0.1:18080/internal/auth/introspect"
    MALL_AGENT_AUTH_TOKEN: str
    TEST_MALL_TOKEN: str | None = None
    MCP_SERVER_URL: str = "http://127.0.0.1:18081/mcp"

    LANGGRAPH_SQLITE_PATH: str = "/data/agent-checkpoints.sqlite"
    CHECKPOINT_BACKEND: Literal["redis", "sqlite"] = "redis"

    REDIS_URL:str ="redis://localhost:6379/0"

    EMBEDDING_MODEL:str
    EMBEDDING_BASE_URL:str
    EMBEDDING_API_KEY:str

    QDRANT_BASE_URL:str
    QDRANT_API_KEY:str
    QDRANT_COLLECTION:str
    RAG_TOP_K:int


    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
