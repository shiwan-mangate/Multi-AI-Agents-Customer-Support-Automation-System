from pydantic_settings import BaseSettings, SettingsConfigDict


class APISettings(BaseSettings):
    API_TITLE: str = "Enterprise CRM & Agent Orchestration API"
    API_VERSION: str = "1.0.0"

    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    ALLOWED_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


api_settings = APISettings()