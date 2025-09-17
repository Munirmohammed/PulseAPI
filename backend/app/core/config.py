from functools import lru_cache
from pydantic import BaseSettings, AnyUrl


class Settings(BaseSettings):
    app_name: str = "PulseAPI Backend"
    secret_key: str = "change_me"
    access_token_expire_minutes: int = 60
    database_url: str

    # Alerts
    smtp_host: str | None = None
    smtp_port: int | None = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    slack_webhook_url: str | None = None

    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str | None = None
    celery_result_backend: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def broker(self) -> str:
        return self.celery_broker_url or self.redis_url

    def backend(self) -> str:
        return self.celery_result_backend or self.redis_url


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


