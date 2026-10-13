from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    app_name: str = "AI Production Incident Investigator"
    app_env: str = "development"
    github_token: SecretStr | None = None  
    database_url: str
    jwt_secret: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()