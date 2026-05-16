from sqlalchemy.orm import Session

from app.infrastructure.db.models import ArticleEvent


def save_article_event(db: Session, event: ArticleEvent) -> None:
    db.add(event)
    db.commit()
