from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import analytics, articles, categories, parties
from app.infrastructure.db.session import engine
from app.infrastructure.db import models
from app.settings import Settings

settings = Settings()

models.Base.metadata.create_all(bind=engine)

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
