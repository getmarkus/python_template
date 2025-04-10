from typing import List, Literal

from pydantic import AnyHttpUrl
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
)
from typing import Type
from functools import lru_cache


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

    @property
    def get_table_schema(self) -> str | None:
        """Return table_schema if database_url does not start with sqlite, otherwise return None."""
        if self.database_url.startswith("sqlite"):
            return None
        return self.database_schema

    @property
    def backend_cors_origins_list(self) -> List[AnyHttpUrl]:
        return [AnyHttpUrl(origin) for origin in self.backend_cors_origins]

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


@lru_cache()
def get_settings() -> "Settings":
    return Settings()
