import os
from functools import lru_cache
from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "LexiCoach English AI Backend"
    debug: bool = False
    cerebras_api_key: str | None = None
    deepgram_api_key: str | None = None
    redis_url: str | None = None
    aws_bucket: str | None = None
    aws_access_key: str | None = None
    aws_secret_key: str | None = None
    aws_region: str = "us-east-1"
    celery_broker_url: str | None = Field(default_factory=lambda: os.getenv("REDIS_URL"))
    celery_result_backend: str | None = Field(default_factory=lambda: os.getenv("REDIS_URL"))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def default_settings() -> Settings:
    return Settings()

settings = default_settings()
