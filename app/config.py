from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    NATS_URL: str = "nats://localhost:4222"
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    EXTERNAL_API_URL: str = "https://example.com/prices"
    FETCH_INTERVAL_SECONDS: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()

