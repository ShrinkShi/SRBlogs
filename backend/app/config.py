from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.version import APP_NAME, GITHUB_REPO


class Settings(BaseSettings):
    app_name: str = f"{APP_NAME} API"
    app_env: str = "development"
    data_dir: str = "backend/data"
    public_base_url: str = "http://127.0.0.1:8000"
    site_start_time: str = ""

    admin_username: str = "admin"
    admin_password: str = ""
    admin_password_hash: str = ""
    jwt_secret: str = "please-change-this-secret"
    jwt_expire_minutes: int = 1440

    cors_origins: str = "http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:5175,http://localhost:5173,http://localhost:5174,http://localhost:5175"

    upload_driver: str = "local"
    upload_max_size: int = 5242880
    upload_allowed_types: str = "image/jpeg,image/png,image/gif,image/webp,audio/mpeg,audio/wav,audio/ogg,audio/mp4,video/mp4,video/webm,video/quicktime"
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

    github_oauth_client_id: str = ""
    github_oauth_client_secret: str = ""
    qq_oauth_app_id: str = ""
    qq_oauth_app_secret: str = ""

    contact_mail_enabled: bool = False
    contact_mail_to: str = "1363072460@qq.com"
    smtp_host: str = ""
    smtp_port: int = 465
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_ssl: bool = True
    smtp_from: str = ""

    srblogs_update_repo: str = GITHUB_REPO
    srblogs_update_enabled: bool = True
    srblogs_update_command: str = ""
    env_file_path: str = "/etc/srblogs/backend.env"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def data_path(self) -> Path:
        path = Path(self.data_dir)
        if not path.is_absolute():
            repo_root = Path(__file__).resolve().parents[2]
            backend_root = repo_root / "backend"
            if path.parts[:2] == ("backend", "data"):
                path = repo_root / path
            elif path.parts[:1] == ("data",):
                path = backend_root / path
            else:
                path = repo_root / path
        return path

    @property
    def cors_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
