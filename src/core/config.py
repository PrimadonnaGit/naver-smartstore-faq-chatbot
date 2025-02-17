import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class BaseAppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "naver-faq-chatbot"
    OPENAI_API_KEY: str
    DEBUG: bool = False

    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["test", "local", "production"]

    EMBEDDING_MODE: Literal["default", "openai"] = "openai"

    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    REDIS_MESSAGE_TTL: int = 10 * 60  # 10분

    CHROMA_PERSIST_DIRECTORY: str = str(ROOT_DIR / "chroma_persist")
    CHROMA_COLLECTION_NAME: str = "smartstore_faqs"

    @computed_field
    def REDIS_URL(cls) -> str:
        return f"redis://{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"


class LocalSettings(BaseAppSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env.local")
    ENVIRONMENT: Literal["test", "local", "production"] = "local"


class TestSettings(BaseAppSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env.test")
    ENVIRONMENT: Literal["test", "local", "production"] = "test"


class ProductionSettings(BaseAppSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env.production")
    ENVIRONMENT: Literal["test", "local", "production"] = "production"


@lru_cache()
def get_settings():
    env = os.getenv("ENVIRONMENT", "local")
    configs = {
        "local": LocalSettings,
        "test": TestSettings,
        "production": ProductionSettings,
    }
    config_class = configs.get(env, LocalSettings)
    return config_class()


settings = get_settings()
