from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://kuni_musubi:kuni_musubi@localhost:5432/kuni_musubi"
    # Gemini API キー（LLM処理に使用）
    gemini_api_key: str = ""
    # LLM モデル名
    llm_model: str = "gemini-3-flash-preview"
    # スクレイパーの HTTP タイムアウト（秒）— 保守的に短めに設定
    scraper_timeout: int = 15
    # RSS フィード取得の最大件数
    rss_max_items: int = 50
    # リクエスト間の最小待機秒数（サーバー負荷対策）
    scraper_request_delay_seconds: float = 3.0
    # 同一ドメインへの連続アクセス間隔（秒）
    scraper_domain_interval_seconds: float = 10.0
    # 1 バッチ実行あたりの最大取得記事数
    scraper_max_items_per_run: int = 30
    # 最大リトライ回数（少なく設定して過負荷を防ぐ）
    scraper_max_retries: int = 1
    # 指数バックオフの乗数
    scraper_backoff_factor: float = 2.0


settings = Settings()
