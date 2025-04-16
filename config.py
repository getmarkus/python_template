from typing import List, Literal

from pydantic import AnyHttpUrl, SecretStr
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
)
from typing import Type
from functools import lru_cache
from urllib.parse import urlparse, parse_qs, quote_plus


class Settings(BaseSettings):
    # Application settings
    project_name: str
    database_url_template: str
    database_schema: str | None = None
    migrate_database: bool = False
    sqlite_wal_mode: bool = False
    database_type: str = "sqlmodel"
    current_env: Literal["testing", "default"]
    app_db_password: SecretStr
    app_db_user: str

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
        Dynamically return the database_url with the password from app_db_password.
        This ensures the database connection always uses the current password from the settings.
        """
        # Get the current password and username from class properties
        current_password = (
            self.app_db_password.get_secret_value() if self.app_db_password else None
        )
        current_username = self.app_db_user

        # If password not found, return the original URL
        if not current_password:
            return self.database_url_template

        # Handle SQLite connections differently
        if self.database_url_template.startswith("sqlite"):
            return self.database_url_template

        try:
            # Split the URL into components
            protocol_part, rest = self.database_url_template.split("://", 1)

            if "@" in rest:
                # Handle URLs with authentication (username:password@host:port/db)
                _, server_part = rest.split("@", 1)

                # Use the username from settings or fall back to default
                username = current_username or "app_user"

                # Reconstruct with current username and password, ensuring password is URL-encoded
                return f"{protocol_part}://{username}:{quote_plus(current_password)}@{server_part}"
            else:
                # For URLs without authentication, use username from settings or default
                username = current_username or "app_user"
                return f"{protocol_part}://{username}:{quote_plus(current_password)}@{rest}"
        except Exception as e:
            # Log the error but don't crash - return original URL as fallback
            print(f"Error generating dynamic database URL: {e}")
            return self.database_url_template

    @property
    def get_db_connection_params(self) -> dict:
        """
        Return a dictionary of database connection parameters.
        Useful for libraries that accept connection parameters as separate arguments.
        """
        # Use the dynamic URL with current password
        url = self.database_url_with_current_password

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
