from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.article import ArticleCardResponse


class PartyResponse(BaseModel):
    id: UUID
    name: str
    short_name: str
    color_hex: Optional[str] = None
    house_of_representatives_seats: Optional[int] = None
    house_of_councillors_seats: Optional[int] = None
    total_seats: int = 0


class PartyDetailResponse(PartyResponse):
    founded_year: Optional[int] = None
    leader_name: Optional[str] = None
    ideology_summary: Optional[str] = None
    manifesto_summary: Optional[str] = None
    manifesto_promises: list[str] = Field(default_factory=list)
    main_policy_categories: list[str] = Field(default_factory=list)
    official_url: Optional[str] = None
    latest_articles: list[ArticleCardResponse] = Field(default_factory=list)
