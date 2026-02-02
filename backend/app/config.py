from typing import Set

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, PostgresDsn, RedisDsn
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class VideoConfig(BaseModel):
    upload_dir: Path = BASE_DIR / "uploads" / "videos"
    max_size: int = 100 * 1024 * 1024  # 100 MB
    allowed_types: Set[str] = {
        "video/mp4",
        "video/avi",
        "video/mkv",
        "video/mov",
        "video/webm",
    }

    def ensure_dirs(self) -> None:
        self.upload_dir.mkdir(parents=True, exist_ok=True)


class DataBaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class AuthConfig(BaseModel):
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    secret_key: str = "supersecret"


class RedisConfig(BaseModel):
    url: RedisDsn
    db: int = 0


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="FASTAPI_CONFIG__",
        extra="ignore",
    )
    db: DataBaseConfig
    redis: RedisConfig
    auth: AuthConfig = AuthConfig()
    video: VideoConfig = VideoConfig()


settings = Settings()

settings.video.ensure_dirs()
