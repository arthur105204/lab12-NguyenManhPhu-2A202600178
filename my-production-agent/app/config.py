from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "My Production Agent"
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000

    redis_url: str = "redis://redis:6379/0"
    agent_api_key: str = "change-me"
    log_level: str = "INFO"

    rate_limit_per_minute: int = 10
    monthly_budget_usd: float = 10.0

    llm_model: str = "mock-llm"
    history_max_items: int = 50


settings = Settings()
