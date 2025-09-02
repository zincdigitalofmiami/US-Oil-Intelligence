from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Union

class Settings(BaseSettings):
    app_name: str = "Soy Intel API"
    env: str = "dev"
    api_prefix: str = "/api"
    port: int = Field(default=8080)
    data_dir: str = "data"
    backend_cors_origins: List[str] = Field(default=["http://localhost", "http://localhost:8080", "https://us-oil-solutions-app.web.app"])

    class Config:
        env_file = ".env"

settings = Settings()
