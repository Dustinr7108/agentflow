"""AgentFlow configuration - environment-based settings."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "AgentFlow"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://agentflow:agentflow@localhost:5433/agentflow"
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI Providers
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    DEFAULT_MODEL: str = "gpt-4o-mini"

    # Auth & Security
    SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_PRICE_STARTER: Optional[str] = None   # $29/mo
    STRIPE_PRICE_PRO: Optional[str] = None        # $99/mo
    STRIPE_PRICE_ENTERPRISE: Optional[str] = None  # $299/mo

    # Usage Limits (per plan per month)
    STARTER_RUNS: int = 100
    PRO_RUNS: int = 1000
    ENTERPRISE_RUNS: int = 10000

    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASS: Optional[str] = None

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
