from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    app_name: str = "Soy Intel API"
    env: str = "dev"
    api_prefix: str = "/api"
    port: int = Field(default=8080)
    data_dir: str = "data"
    cors_allow_origins: str = "*"
    class Config:
        env_file = ".env"

settings = Settings()
