from functools import lru_cache
from typing import List

from dynaconf import Dynaconf, Validator
from pydantic import AnyHttpUrl

# order matters
# [default] settings in settings.toml are loaded first
# [APP_ENV] settings override defaults
# .env file overrides those
# Environment variables have the highest priority
# CLI arguments override those

settings = Dynaconf(
    envvar_prefix="APP",
    settings_files=["settings.toml", ".secrets.toml"],
    environments=True,
    load_dotenv=True,
    validators=[
        Validator("database_url", must_exist=True),
        Validator("project_name", must_exist=True),
        Validator("migrate_database", is_type_of=bool),
        Validator("backend_cors_origins", is_type_of=list),
    ],
)


# Singleton pattern to ensure only one settings instance
@lru_cache()
def get_settings():
    return settings


# Type hints for your settings (optional but recommended)
class Settings:
    project_name: str
    database_url: str
    migrate_database: bool
    backend_cors_origins: List[AnyHttpUrl]
    execution_mode: str
    env_smoke_test: str
