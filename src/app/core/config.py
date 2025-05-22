from pydantic import validator, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Price Tracker API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENVIRONMENT: str = "development"  # Can be "local", "development", "production"
    DATABASE_URL: PostgresDsn
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    KAFKA_BROKER_URL: str = "localhost:9092"
    CELERY_BROKER_URL: RedisDsn = "redis://localhost:6379/0" # type: ignore
    CELERY_RESULT_BACKEND: RedisDsn = "redis://localhost:6379/0" # type: ignore

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @validator("SECRET_KEY")
    def validate_secret_key(cls, v: str, values: dict) -> str:
        if values.get("ENVIRONMENT") == "production" and not v:
            raise ValueError("SECRET_KEY must be set in production environment")
        return v

    @validator("DATABASE_URL")
    def validate_database_url(cls, v: PostgresDsn, values: dict) -> PostgresDsn:
        if values.get("ENVIRONMENT") == "production" and not v:
            raise ValueError("DATABASE_URL must be set in production environment")
        return v

settings = Settings()
