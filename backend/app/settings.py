from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://kuni_musubi:kuni_musubi@localhost:5432/kuni_musubi"
    cors_origins: list[str] = ["http://localhost:3000"]
