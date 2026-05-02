from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.infrastructure.db.session import get_db
from app.schemas.article import ArticleDetailResponse, ArticleListResponse
from app.usecases import get_article_detail, list_articles

router = APIRouter(prefix="/articles", tags=["articles"])

ALLOWED_SORT_VALUES = {"latest", "important"}
MAX_LIMIT = 50


@router.get("", response_model=ArticleListResponse)
def get_articles(
    db: Annotated[Session, Depends(get_db)],
    party_id: UUID | None = Query(default=None),
    category_ids: str | None = Query(default=None),
    sort: str = Query(default="latest"),
    limit: int = Query(default=20, ge=1, le=MAX_LIMIT),
    cursor: str | None = Query(default=None),
) -> ArticleListResponse:
    if sort not in ALLOWED_SORT_VALUES:
        raise HTTPException(status_code=422, detail=f"sort must be one of {ALLOWED_SORT_VALUES}")
    parsed_category_ids = category_ids.split(",") if category_ids else []
    return list_articles.execute(
        db,
        party_id=party_id,
        category_ids=parsed_category_ids,
        sort=sort,
        limit=limit,
        cursor=cursor,
    )


@router.get("/{article_id}", response_model=ArticleDetailResponse)
def get_article(
    article_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> ArticleDetailResponse:
    article = get_article_detail.execute(db, article_id=article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article
