import tomllib
from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


# https://fastapi.tiangolo.com/advanced/settings/
# https://docs.pydantic.dev/latest/concepts/pydantic_settings/
# https://docs.pydantic.dev/latest/concepts/pydantic_settings/#command-line-support
class Settings(BaseSettings):
    # https://stackoverflow.com/questions/70852331/how-to-define-class-attributes-after-inheriting-pydantics-basemodel
    # https://stackoverflow.com/questions/69388833/triggering-a-function-on-creation-of-an-pydantic-object
    pyproject_file: str = ""
    execution_mode: str = ""
    env_smoke_test: str = ""
    project_name: str = ""
    database_url: str = "sqlite:///./issues.db"
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    backend_cors_origins: List[AnyHttpUrl] = []

    model_config = SettingsConfigDict(env_file=".env", extra="allow")
    # `.env.prod` takes priority over `.env`
    #   env_file=('.env', '.env.prod')

    def setFromTOML(self):
        with open(self.pyproject_file, "rb") as f:
            _META = tomllib.load(f)
        self.project_name = _META["project"]["name"]

    @classmethod
    @lru_cache
    def get_settings(cls):
        settings = Settings(pyproject_file="pyproject.toml")
        settings.setFromTOML()
        return settings
