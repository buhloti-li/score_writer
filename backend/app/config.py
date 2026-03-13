from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/scorewriter"
    database_echo: bool = False

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Meilisearch
    meilisearch_url: str = "http://localhost:7700"
    meilisearch_key: str = "dev-master-key"

    # Auth
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Storage
    oss_enabled: bool = False
    local_storage_path: str = "./storage"

    # LLM
    anthropic_api_key: str = ""

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    # App
    app_name: str = "Score Writer"
    debug: bool = True
    max_upload_size: int = 20 * 1024 * 1024  # 20MB

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
