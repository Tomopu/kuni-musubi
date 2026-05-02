from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.infrastructure.db.session import get_db
from app.schemas.analytics import ArticleEventRequest, OnboardingEventRequest
from app.usecases import record_article_event, record_onboarding_event

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/onboarding", status_code=204)
def post_onboarding_event(
    payload: OnboardingEventRequest,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    record_onboarding_event.execute(db, payload=payload)


@router.post("/article-event", status_code=204)
def post_article_event(
    payload: ArticleEventRequest,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    record_article_event.execute(db, payload=payload)
