"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Application
    APP_NAME: str = "Secure File Storage API"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "Store files securely with AES-256-GCM encryption."
    DEBUG: bool = False

    # API
    API_PREFIX: str = "/api"

    # Database
    DATABASE_URL: str = "sqlite:///./secure_storage.db"

    # Authentication
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Cryptography
    RSA_KEY_SIZE: int = 2048

    # Storage
    STORAGE_PATH: str = "storage/encrypted_files"
    MAX_UPLOAD_SIZE_MB: int = 100

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"

    @property
    def cors_origin_list(self) -> list[str]:
        """CORS origins parsed from the comma-separated setting."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def max_upload_size_bytes(self) -> int:
        """Maximum upload size in bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()


settings = get_settings()
