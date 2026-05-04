from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ArticleThumbnail(BaseModel):
    type: str
    text: str | None
    url: str | None


class ArticleCategoryResponse(BaseModel):
    id: UUID
    name: str


class ArticlePartyResponse(BaseModel):
    id: UUID
    name: str
    short_name: str
    color_hex: str


class ArticleCardResponse(BaseModel):
    id: UUID
    display_title: str
    card_summary: str
    thumbnail: ArticleThumbnail
    parties: list[ArticlePartyResponse]
    categories: list[ArticleCategoryResponse]
    published_at: datetime


class ArticleSourceResponse(BaseModel):
    source_name: Optional[str] = None
    source_url: str
    published_at: Optional[datetime] = None
    retrieved_at: Optional[datetime] = None


class ArticleDisplayContentResponse(BaseModel):
    positive_point: str
    life_impact: str
    remaining_issues: list[str]
    public_reactions_summary: Optional[str] = None


class ArticleDetailResponse(ArticleCardResponse):
    display_content: ArticleDisplayContentResponse | None
    sources: list[ArticleSourceResponse]


class ArticleListResponse(BaseModel):
    items: list[ArticleCardResponse]
    next_cursor: str | None
