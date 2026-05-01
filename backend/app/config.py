from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SRBlogs API"
    app_env: str = "development"
    data_dir: str = "backend/data"
    public_base_url: str = "http://127.0.0.1:8000"

    admin_username: str = "admin"
    admin_password: str = "change-me"
    jwt_secret: str = "please-change-this-secret"
    jwt_expire_minutes: int = 1440

    cors_origins: str = "http://127.0.0.1:5173,http://127.0.0.1:5174,http://localhost:5173,http://localhost:5174"

    upload_driver: str = "local"
    oss_access_key_id: str = ""
    oss_access_key_secret: str = ""
    oss_bucket: str = ""
    oss_endpoint: str = ""
    oss_public_base_url: str = ""

    ai_a_base_url: str = ""
    ai_a_api_key: str = ""
    ai_a_model: str = ""
    ai_b_base_url: str = ""
    ai_b_api_key: str = ""
    ai_b_model: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def data_path(self) -> Path:
        path = Path(self.data_dir)
        if not path.is_absolute():
            path = Path.cwd() / path
        return path

    @property
    def cors_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
