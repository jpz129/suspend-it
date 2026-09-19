from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "sqlite:///./app.db"
    JWT_SECRET: str = "change-me"
    ANTHROPIC_API_KEY: str = ""
    WGER_API_BASE: str = "https://wger.de/api/v2"


settings = Settings()
