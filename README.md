# kuni-musubi

第2期 北海道 火-Okoshi 制作

## 開発環境のセットアップ

Claude Code を Docker サンドボックス内で使う場合は、先に `docs/development/README.md` を参照してください。

### 前提

- Docker / Docker Compose
- Node.js 22+
- Python 3.12+
- uv

### 構成

```
frontend/   Next.js / TypeScript  (ローカル起動)
backend/    FastAPI / Python      (Docker Compose)
batch/      Python batch workers
docs/       設計ドキュメント
```

---

## バックエンド・DB の起動（Docker Compose）

```bash
# backend と db を起動する
docker compose up -d

# ログを確認する
docker compose logs -f backend

# 停止する
docker compose down
```

- DB: `localhost:5432` (PostgreSQL 16)
- API: `http://localhost:8000`
- ヘルスチェック: `http://localhost:8000/health`
- API ドキュメント: `http://localhost:8000/docs`

### ダミーデータ

開発環境では backend 起動時に、政党、政策カテゴリ、デモ記事が自動投入されます。
投入処理は固定 ID を使った冪等処理のため、backend を再起動しても同じ記事が重複作成されません。

```bash
# DB volume を残してコンテナだけ削除する。ダミーデータは残る。
docker compose down

# DB volume ごと削除する。次回 backend 起動時にダミーデータが再投入される。
docker compose down -v
docker compose up -d
```

自動投入を止めたい場合は、backend の環境変数 `AUTO_SEED_DEMO_DATA=false` を設定してください。

---

## フロントエンドの起動（ローカル）

```bash
cd frontend

# 初回のみ: 環境変数を設定する
cp .env.local.example .env.local

# 依存をインストールする
npm install

# 開発サーバーを起動する
npm run dev
```

- フロントエンド: `http://localhost:3000`

### 型チェック・Lint

```bash
cd frontend
npm run typecheck
npm run lint
```

---

## バックエンドの開発（ローカル直接起動）

Docker Compose を使わずにローカルで直接起動する場合:

```bash
cd backend

# 仮想環境を作成してパッケージをインストールする
uv venv
uv pip install -e ".[dev]"

# 環境変数を設定する
cp ../.env.example .env
# .env の DATABASE_URL を必要に応じて編集する

# サーバーを起動する
uv run uvicorn app.main:app --reload
```

### 型チェック・Lint

```bash
cd backend
uv run ruff check .
uv run mypy .
uv run pytest
```

---

## バッチの開発

```bash
cd batch

uv venv
uv pip install -e ".[dev]"

uv run pytest
```

---

## Docker Compose でフロントエンドも含めて起動する場合

```bash
docker compose --profile full up -d
```

---

## 環境変数

`.env.example` を参照してください。

| 変数名 | 説明 | デフォルト |
|---|---|---|
| `DATABASE_URL` | PostgreSQL 接続文字列 | `postgresql://kuni_musubi:kuni_musubi@localhost:5432/kuni_musubi` |
| `CORS_ORIGINS` | 許可する CORS オリジン（JSON 配列） | `["http://localhost:3000"]` |
| `AUTO_SEED_DEMO_DATA` | 開発用の政党、カテゴリ、デモ記事を起動時に投入するか | `true` |
| `NEXT_PUBLIC_API_BASE_URL` | フロントエンドから見た API の URL | `http://localhost:8000` |
