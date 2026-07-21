"""Application configuration via pydantic-settings."""

from pydantic_settings import BaseSettings


def parse_cors_origins(raw: str) -> list[str]:
    """Parse comma-separated CORS_ORIGINS string into a list."""
    return [o.strip() for o in raw.split(",") if o.strip()]


class Settings(BaseSettings):
    """StockWise backend settings loaded from environment variables."""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    # Anthropic
    ANTHROPIC_API_KEY: str
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"

    # External APIs (all optional — system degrades gracefully)
    ALPHA_VANTAGE_API_KEY: str = ""

    # App
    CORS_ORIGINS: str = "http://localhost:3000"
    DATABASE_URL: str = "sqlite+aiosqlite:///./stockwise.db"
    CACHE_TTL_SECONDS: int = 300

    # Deployment
    ENVIRONMENT: str = "development"  # "development" or "production"

    # Rate limiting
    YFINANCE_RATE_LIMIT: float = 2.0
    SEC_EDGAR_RATE_LIMIT: float = 0.1


settings = Settings()
