from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import analytics, articles, categories, parties
from app.infrastructure.db import models
from app.infrastructure.db.dev_schema import ensure_dev_schema
from app.infrastructure.db.seeds.run_seeds import run as run_seeds
from app.infrastructure.db.session import engine
from app.settings import Settings

settings = Settings()

models.Base.metadata.create_all(bind=engine)
ensure_dev_schema(engine)

if settings.auto_seed_demo_data:
    run_seeds()

app = FastAPI(title="Kuni-Musubi API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(articles.router)
app.include_router(parties.router)
app.include_router(categories.router)
app.include_router(analytics.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
