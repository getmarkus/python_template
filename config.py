from typing import List, Literal

from pydantic import AnyHttpUrl
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
)
from typing import Type
from functools import lru_cache
from urllib.parse import urlparse, parse_qs


class Settings(BaseSettings):
    # Application settings
    project_name: str
    database_url_template: str
    database_schema: str | None = None
    create_tables: bool = False
    sqlite_wal_mode: bool = False
    database_type: str = "sqlmodel"
    current_env: Literal["testing", "default"]
    # Database credentials removed - now included directly in database_url_template

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
        if self.database_url_template.startswith("sqlite"):
            return None
        return self.database_schema

    @property
    def backend_cors_origins_list(self) -> List[AnyHttpUrl]:
        return [AnyHttpUrl(origin) for origin in self.backend_cors_origins]

    @property
    def database_url(self) -> str:
        """
        Return the database URL template directly without modification.
        The connection string should include all necessary credentials in the template.
        """
        return self.database_url_template

    @property
    def is_async_database(self) -> bool:
        """
        Determine if the database URL is configured for asynchronous connections.
        Returns True if the URL contains async drivers like asyncpg or aiosqlite.
        """
        url = self.database_url_template.lower()
        return "+asyncpg" in url or "+aiosqlite" in url or self.database_url_template.startswith("postgresql+asyncpg")

    @property
    def get_db_connection_params(self) -> dict:
        """
        Return a dictionary of database connection parameters.
        Useful for libraries that accept connection parameters as separate arguments.
        """
        # Use the dynamic URL with current password
        url = self.database_url

        if url.startswith("sqlite"):
            # Handle SQLite connections
            path = url.replace("sqlite:///", "")
            return {
                "database": path if path != ":memory:" else ":memory:",
                "database_type": "sqlite",
            }

        try:
            # Parse the URL to extract components
            parsed = urlparse(url)

            # Extract username and password from netloc
            userpass, hostport = (
                parsed.netloc.split("@", 1)
                if "@" in parsed.netloc
                else ("", parsed.netloc)
            )
            username, password = (
                userpass.split(":", 1) if ":" in userpass else (userpass, "")
            )

            # Extract host and port
            host, port = hostport.split(":", 1) if ":" in hostport else (hostport, "")

            # Extract database name from path
            database = parsed.path.lstrip("/")

            # Extract query parameters
            params = parse_qs(parsed.query)

            result = {
                "username": username,
                "password": password,
                "host": host,
                "port": int(port) if port.isdigit() else None,
                "database": database,
                "database_type": parsed.scheme.split("+")[0]
                if "+" in parsed.scheme
                else parsed.scheme,
                "driver": parsed.scheme.split("+")[1] if "+" in parsed.scheme else None,
            }

            # Add schema if available
            if self.database_schema:
                result["schema"] = self.database_schema

            # Add query parameters
            for key, values in params.items():
                if len(values) == 1:
                    result[key] = values[0]
                else:
                    result[key] = values

            return result
        except Exception as e:
            # Log the error but don't crash - return minimal dict as fallback
            print(f"Error parsing database URL: {e}")
            return {"database_url": url}

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
