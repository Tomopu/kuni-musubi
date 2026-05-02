from sqlalchemy.orm import Session

from app.infrastructure.db.models import ArticleEvent
from app.schemas.analytics import ArticleEventRequest


def execute(db: Session, *, payload: ArticleEventRequest) -> None:
    event = ArticleEvent(
        event_type=payload.event_type,
        article_id=payload.article_id,
        surface=payload.surface,
    )
    db.add(event)
    db.commit()
