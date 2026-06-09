import json
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://researchmind:researchmind_secret@localhost:5432/researchmind"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    google_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    embedding_model: str = "models/gemini-embedding-001"

    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    cors_origins: str = "http://localhost:3000"
    environment: str = "development"

    upload_dir: str = "./data/uploads"
    faiss_dir: str = "./data/faiss"
    max_upload_size_mb: int = 50
    max_papers_per_user: int = 100

    rate_limit_per_minute: int = 60

    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_top_k: int = 8
    rerank_top_k: int = 5

    @property
    def cors_origin_list(self) -> list[str]:
        value = self.cors_origins.strip()
        if value.startswith("["):
            try:
                origins = json.loads(value)
                if isinstance(origins, list):
                    return [str(origin).strip() for origin in origins if str(origin).strip()]
            except json.JSONDecodeError:
                pass
        return [origin.strip() for origin in value.split(",") if origin.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
