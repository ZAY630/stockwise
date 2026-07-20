"""Application configuration via pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """StockWise backend settings loaded from environment variables."""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # Anthropic
    ANTHROPIC_API_KEY: str
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"

    # External APIs (all optional — system degrades gracefully)
    ALPHA_VANTAGE_API_KEY: str = ""

    # App
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    DATABASE_URL: str = "sqlite+aiosqlite:///./stockwise.db"
    CACHE_TTL_SECONDS: int = 300

    # Rate limiting
    YFINANCE_RATE_LIMIT: float = 2.0
    SEC_EDGAR_RATE_LIMIT: float = 0.1


settings = Settings()
