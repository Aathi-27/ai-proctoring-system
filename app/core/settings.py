from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="INTEGRITY_", extra="ignore")

    mongo_dsn: str | None = None
    mongo_db: str = "integrity"

    default_retention_days: int = 30

    enable_retention_sweep: bool = False
    retention_sweep_interval_seconds: int = 3600


settings = Settings()
