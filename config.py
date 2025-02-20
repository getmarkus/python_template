from functools import lru_cache
from typing import List, Literal

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application settings
    project_name: str
    database_url: str
    database_schema: str | None = None
    migrate_database: bool = False
    sqlite_wal_mode: bool = False
    database_type: str = "sqlmodel"
    current_env: Literal["testing", "default"]

    # CORS settings
    backend_cors_origins: List[str] = ["http://localhost:8000", "http://localhost:3000"]
    cors_allow_credentials: bool = False
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = [
        "X-Forwarded-For",
        "Authorization",
        "Content-Type",
        "X-Request-ID",
    ]
    cors_expose_headers: List[str] = ["X-Process-Time", "X-Request-ID"]

    # Configure environment variable loading
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("database_schema")
    def validate_schema(cls, v: str | None, values) -> str | None:
        # Only set database_schema if database_url doesn't start with sqlite
        if values.data.get("database_url", "").startswith("sqlite"):
            return None
        return v

    @property
    def backend_cors_origins_list(self) -> List[AnyHttpUrl]:
        return [AnyHttpUrl(origin) for origin in self.backend_cors_origins]


# Singleton pattern to ensure only one settings instance
@lru_cache()
def get_settings() -> "Settings":
    return Settings()
