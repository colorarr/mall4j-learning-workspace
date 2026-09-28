from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"

if __name__ == "__main__":
    print(ENV_PATH)


class Settings(BaseSettings):
    MODEL_NAME: str
    BASE_URL: str
    API_KEY: str
    TAVILY_API_KEY:str
    REDIS_URL: str

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()