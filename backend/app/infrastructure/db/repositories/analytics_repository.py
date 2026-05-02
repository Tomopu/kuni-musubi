from sqlalchemy.orm import Session

from app.infrastructure.db.models import ArticleEvent, OnboardingEvent


def save_onboarding_event(db: Session, event: OnboardingEvent) -> None:
    db.add(event)
    db.commit()


def save_article_event(db: Session, event: ArticleEvent) -> None:
    db.add(event)
    db.commit()
