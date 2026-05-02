from uuid import UUID

from sqlalchemy.orm import Session

from app.schemas.article import ArticleListResponse


def execute(
    db: Session,
    *,
    party_id: UUID | None,
    category_ids: list[str],
    sort: str,
    limit: int,
    cursor: str | None,
) -> ArticleListResponse:
    return ArticleListResponse(items=[], next_cursor=None)
