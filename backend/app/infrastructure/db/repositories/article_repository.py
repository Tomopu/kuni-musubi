from uuid import UUID

from sqlalchemy.orm import Session

from app.infrastructure.db.models import Article


def find_by_id(db: Session, article_id: UUID) -> Article | None:
    return db.query(Article).filter(Article.id == article_id).first()


def find_all(
    db: Session,
    *,
    limit: int,
    offset: int = 0,
) -> list[Article]:
    return db.query(Article).filter(Article.is_published.is_(True)).order_by(Article.published_at.desc()).limit(limit).offset(offset).all()
