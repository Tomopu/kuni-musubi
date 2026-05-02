from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ArticleThumbnail(BaseModel):
    type: str
    text: str | None
    url: str | None


class ArticleParty(BaseModel):
    id: UUID
    name: str
    short_name: str


class ArticleCardResponse(BaseModel):
    id: UUID
    display_title: str
    card_summary: str
    thumbnail: ArticleThumbnail
    parties: list[ArticleParty]
    categories: list[str]
    published_at: datetime


class ArticleDisplayContentResponse(BaseModel):
    positive_point: str
    life_impact: str
    remaining_issues: str
    public_opinion: str


class ArticleDetailResponse(ArticleCardResponse):
    display_content: ArticleDisplayContentResponse | None
    sources: list[str]


class ArticleListResponse(BaseModel):
    items: list[ArticleCardResponse]
    next_cursor: str | None
