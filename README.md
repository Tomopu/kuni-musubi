# kuni-musubi

第2期 北海道 火-Okoshi 制作

Kuni-Musubi は、政治の Good News をわかりやすく届けるニュースアプリです。政党公式サイトなどの一次情報をバッチ処理で取得し、Gemini で記事カード・記事詳細向けの表示文言に整形して、Next.js フロントエンドと FastAPI API で表示します。

## 構成

```txt
frontend/   Next.js / TypeScript
backend/    FastAPI / SQLAlchemy / PostgreSQL
batch/      Python batch workers / Gemini / scraping
docs/       product, research, technical documents
```

主な技術:

- Frontend: Next.js 15, React 19, TypeScript, lucide-react
- Backend: FastAPI, SQLAlchemy, PostgreSQL 16
- Batch: Python 3.12, uv, httpx, BeautifulSoup, google-genai
- Infrastructure: Docker Compose

## クイックスタート

### 1. Backend と DB を起動

```bash
docker compose up -d
```

起動後に使う URL:

| 用途 | URL |
|---|---|
| API | `http://localhost:8000` |
| Health check | `http://localhost:8000/health` |
| Swagger UI | `http://localhost:8000/docs` |
| Admin | `http://localhost:8000/admin` |
| PostgreSQL | `localhost:5432` |

backend 起動時に、政党、政策カテゴリ、デモ記事が自動投入されます。自動投入を止める場合は `AUTO_SEED_DEMO_DATA=false` を設定してください。

### 2. Frontend を起動

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

Frontend は `http://localhost:3000` で起動します。

### 3. Admin ユーザーを作成

```bash
cd backend
uv run python scripts/create_admin.py --username admin --password yourpassword
```

`http://localhost:8000/admin/login` からログインできます。

## 開発コマンド

### Docker Compose

```bash
# backend と db を起動
docker compose up -d

# frontend も Docker で起動
docker compose --profile full up -d

# ログ確認
docker compose logs -f backend

# コンテナ停止
docker compose down

# DB volume ごと削除して初期化
docker compose down -v
```

### Frontend

```bash
cd frontend
npm run dev
npm run typecheck
npm run lint
```

### Backend

Docker Compose を使わずに backend を直接起動する場合:

```bash
cd backend
uv venv
uv pip install -e ".[dev]"
cp ../.env.example .env
uv run uvicorn app.main:app --reload
```

検証:

```bash
cd backend
uv run ruff check .
uv run mypy .
uv run pytest
```

### Batch

```bash
cd batch
uv venv
uv pip install -e ".[dev]"
```

スクレイピングだけ確認:

```bash
PYTHONPATH=..:../backend uv run python -m batch.main --fetch-only
```

Gemini による LLM 処理まで確認し、DB には保存しない:

```bash
PYTHONPATH=..:../backend uv run python -m batch.main --dry-run
```

通常実行。RSS/HTML 取得、本文補強、Gemini 処理、DB 保存まで実行:

```bash
PYTHONPATH=..:../backend uv run python -m batch.main
```

RSS フィードを自動探索して `batch/config/parties.yml` の更新候補を生成:

```bash
cd batch
uv run python verify_feeds.py
```

## 環境変数

`.env.example` と `frontend/.env.local.example` を参照してください。

| 変数名 | 用途 | デフォルト |
|---|---|---|
| `DATABASE_URL` | PostgreSQL 接続文字列 | `postgresql://kuni_musubi:kuni_musubi@localhost:5432/kuni_musubi` |
| `CORS_ORIGINS` | backend が許可する CORS origin | `["http://localhost:3000"]` |
| `AUTO_SEED_DEMO_DATA` | backend 起動時に開発用データを投入するか | `true` |
| `ADMIN_SECRET_KEY` | Admin セッション署名用 secret | 開発用固定値 |
| `NEXT_PUBLIC_API_BASE_URL` | frontend から見た API URL | `http://localhost:8000` |
| `GEMINI_API_KEY` | Gemini API キー。`--fetch-only` 以外の batch 実行で必要 | なし |
| `LLM_MODEL` | Gemini モデル名 | `gemini-3-flash-preview` |
| `SCRAPER_TIMEOUT` | HTTP タイムアウト秒数 | `15` |
| `RSS_MAX_ITEMS` | RSS フィードあたりの最大取得件数 | `50` |
| `SCRAPER_REQUEST_DELAY_SECONDS` | リクエスト間の最小待機秒数 | `3.0` |
| `SCRAPER_DOMAIN_INTERVAL_SECONDS` | 同一ドメインへの連続アクセス間隔 | `10.0` |
| `SCRAPER_MAX_ITEMS_PER_RUN` | 1バッチあたりの最大処理記事数 | `30` |
| `SCRAPER_MAX_RETRIES` | HTTP エラー時の最大リトライ回数 | `1` |
| `SCRAPER_BACKOFF_FACTOR` | 指数バックオフの乗数 | `2.0` |

`GEMINI_API_KEY` はリポジトリ内に置かず、ローカルの外部設定ファイルやシェル環境変数から読み込んでください。

## 設定ファイル・データの入口

よく触る設定やデータは以下です。

| 種類 | ファイル |
|---|---|
| Gemini システムプロンプト | [batch/llm/prompts/system_prompt.txt](batch/llm/prompts/system_prompt.txt) |
| Gemini ユーザープロンプト | [batch/llm/prompts/user_prompt.txt](batch/llm/prompts/user_prompt.txt) |
| プロンプト読み込みコード | [batch/llm/prompts/article.py](batch/llm/prompts/article.py) |
| LLM 出力スキーマ | [batch/llm/schemas/article.py](batch/llm/schemas/article.py) |
| 政党公式サイト/RSS/HTML取得設定 | [batch/config/parties.yml](batch/config/parties.yml) |
| RSS 自動探索スクリプト | [batch/verify_feeds.py](batch/verify_feeds.py) |
| RSS スクレイパー | [batch/scrapers/rss.py](batch/scrapers/rss.py) |
| HTML 一覧スクレイパー | [batch/scrapers/html_index_scraper.py](batch/scrapers/html_index_scraper.py) |
| 記事本文抽出 | [batch/scrapers/html_parser.py](batch/scrapers/html_parser.py) |
| robots.txt / rate limit | [batch/scrapers/safety.py](batch/scrapers/safety.py) |
| 政党データの元 JSON | [docs/research/data/20260504_government_data.json](docs/research/data/20260504_government_data.json) |
| 政党シード変換 | [backend/app/infrastructure/db/seeds/parties.py](backend/app/infrastructure/db/seeds/parties.py) |
| 政策カテゴリシード | [backend/app/infrastructure/db/seeds/policy_categories.py](backend/app/infrastructure/db/seeds/policy_categories.py) |
| ダミー記事データ | [backend/app/infrastructure/db/seeds/demo_articles.py](backend/app/infrastructure/db/seeds/demo_articles.py) |
| シード実行 | [backend/app/infrastructure/db/seeds/run_seeds.py](backend/app/infrastructure/db/seeds/run_seeds.py) |
| DB モデル | [backend/app/infrastructure/db/models.py](backend/app/infrastructure/db/models.py) |
| Backend 設定 | [backend/app/settings.py](backend/app/settings.py) |
| Batch 設定 | [batch/settings.py](batch/settings.py) |
| Frontend API 接続設定例 | [frontend/.env.local.example](frontend/.env.local.example) |
| Docker Compose | [docker-compose.yml](docker-compose.yml) |

## ドキュメント

| 種類 | ファイル |
|---|---|
| 技術ドキュメント一覧 | [docs/technical/README.md](docs/technical/README.md) |
| DB テーブルまとめ | [docs/technical/20260508_DBテーブルまとめ.md](docs/technical/20260508_DBテーブルまとめ.md) |
| API 設計 | [docs/technical/20260501_API設計.md](docs/technical/20260501_API設計.md) |
| LLM 出力スキーマ設計 | [docs/technical/20260501_LLM出力スキーマ設計.md](docs/technical/20260501_LLM出力スキーマ設計.md) |
| バッチ処理運用ガイド | [docs/technical/20260506_バッチ処理運用ガイド.md](docs/technical/20260506_バッチ処理運用ガイド.md) |
| バッチ処理拡張ガイド | [docs/technical/20260506_バッチ処理拡張ガイド.md](docs/technical/20260506_バッチ処理拡張ガイド.md) |
| プロダクトドキュメント一覧 | [docs/product/README.md](docs/product/README.md) |
| リサーチドキュメント一覧 | [docs/research/README.md](docs/research/README.md) |
| Devcontainer / Docker サンドボックス | [docs/development/README.md](docs/development/README.md) |

## データ保存の概要

通常の batch 実行では、Gemini の JSON 出力を以下の DB テーブルに保存します。

```txt
articles
article_display_contents
article_sources
article_parties
article_categories
```

`--dry-run` は LLM 出力の検証だけ行い、DB には保存しません。

フロントエンドから送信される匿名イベントは、`onboarding_events`, `article_events`, `daily_article_stats` に保存されます。ユーザーアカウント、個人 ID、端末 ID、個人別閲覧履歴は保存しません。
