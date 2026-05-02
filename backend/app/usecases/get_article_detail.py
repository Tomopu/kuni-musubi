from uuid import UUID

from sqlalchemy.orm import Session

from app.schemas.article import ArticleDetailResponse


def execute(db: Session, *, article_id: UUID) -> ArticleDetailResponse | None:
    return None
