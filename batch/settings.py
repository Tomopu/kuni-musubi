from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://kuni_musubi:kuni_musubi@localhost:5432/kuni_musubi"
    # Anthropic API キー（LLM処理に使用）
    anthropic_api_key: str = ""
    # LLM モデル名
    llm_model: str = "claude-haiku-4-5-20251001"
    # スクレイパーの HTTP タイムアウト（秒）
    scraper_timeout: int = 30
    # RSS フィード取得の最大件数
    rss_max_items: int = 50


settings = Settings()
