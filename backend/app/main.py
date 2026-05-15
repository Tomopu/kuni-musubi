import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import analytics, articles, categories, parties
from app.api.admin.router import router as admin_router
from app.infrastructure.db import models
from app.infrastructure.db.dev_schema import ensure_dev_schema
from app.infrastructure.db.seeds.run_seeds import run as run_seeds
from app.infrastructure.db.session import engine
from app.settings import Settings

settings = Settings()
skip_db_init = os.getenv("SKIP_DB_INIT", "").lower() in {"1", "true", "yes"}

if not skip_db_init:
    models.Base.metadata.create_all(bind=engine)
    ensure_dev_schema(engine)

if settings.auto_seed_demo_data and not skip_db_init:
    run_seeds()


@asynccontextmanager
async def lifespan(app_: FastAPI):
    # startup: ゾンビジョブをリカバリする
    if not skip_db_init:
        from app.api.admin.import_service import recover_stale_jobs
        n = recover_stale_jobs()
        if n:
            print(f"[startup] ゾンビジョブをリカバリしました: {n} 件")
    yield


app = FastAPI(title="Kuni-Musubi API", version="0.1.0", lifespan=lifespan)

_cors_origins = list(settings.cors_origins)
if settings.frontend_url and settings.frontend_url not in _cors_origins:
    _cors_origins.append(settings.frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(articles.router)
app.include_router(parties.router)
app.include_router(categories.router)
app.include_router(analytics.router)
app.include_router(admin_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
