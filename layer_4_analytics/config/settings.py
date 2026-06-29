from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ==========================================
    # Database
    # ==========================================
    db_user: str = "postgres"
    db_pass: str
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "customer_support_ai"

    # ==========================================
    # SMTP
    # ==========================================
    SMTP_PASSWORD: str
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_SENDER: str

    # ==========================================
    # LLM / Observability
    # ==========================================
    GROQ_API_KEY: str
    LANGCHAIN_API_KEY: str
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_PROJECT: str = "multi-agent-support-system"

     ## SLACK WEBHOOK
    SLACK_WEBHOOK_URL = str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()