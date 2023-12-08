import tomllib
from typing import List

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


# https://fastapi.tiangolo.com/advanced/settings/
# https://docs.pydantic.dev/latest/concepts/pydantic_settings/
class Settings(BaseSettings):
    execution_mode: str = ""
    env_smoke_test: str = ""
    project_name: str = ""
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    backend_cors_origins: List[AnyHttpUrl] = []

    def setFromTOML(self, tomlFile: str):
        with open("pyproject.toml", "rb") as f:
            _META = tomllib.load(f)
        self.project_name = _META["tool"]["poetry"]["name"]


settings = Settings()
settings.setFromTOML("pyproject.toml")
