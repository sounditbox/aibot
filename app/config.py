from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///database/aibot.database"
    REDIS_URL: str = "redis://localhost:6379/0"

    TELERGAM_API_ID: Optional[int] = None
    TELERGAM_API_HASH: Optional[str] = None
    TELERGAM_SESSION_NAME: str = "aibot_session"
    TELERGAM_CHANNEL_USERNAME: Optional[str] = None

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    PARSE_INTERVAL_MINUTES: int = 1

    DEBUG: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()  # noqa
