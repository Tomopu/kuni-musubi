FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

# 1. 依存定義だけを先にコピーしてインストールする（レイヤキャッシュ最適化）
COPY backend/pyproject.toml .
RUN uv pip install --system --no-cache -r pyproject.toml

# 2. ソースコードとシードデータをコピーする
COPY backend/ .
COPY docs/research/data/ docs/research/data/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
