import os
from functools import lru_cache
from pydantic import BaseSettings, AnyUrl, Field

class Settings(BaseSettings):
    app_name: str = "LexiCoach English AI Backend"
    debug: bool = False
    cerebras_api_key: str
    deepgram_api_key: str
    database_url: AnyUrl
    redis_url: str
    mongo_url: str
    aws_bucket: str
    aws_access_key: str
    aws_secret_key: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_seconds: int = 3600
    aws_region: str = "us-east-1"
    celery_broker_url: str = Field(default_factory=lambda: os.getenv("REDIS_URL"))
    celery_result_backend: str = Field(default_factory=lambda: os.getenv("REDIS_URL"))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
default_settings() -> Settings:
    return Settings()

settings = default_settings()
