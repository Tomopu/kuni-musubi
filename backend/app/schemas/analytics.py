from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

ALLOWED_AGE_GROUPS = {"10s", "20s", "30s", "40s", "50s", "60s", "70s_plus"}
ALLOWED_EVENT_TYPES = {"impression", "card_click", "detail_view", "helpful_click", "source_click"}
ALLOWED_SURFACES = {"home", "party_tab", "party_detail", "article_detail"}
MAX_INTEREST_CATEGORY_IDS = 20


class OnboardingEventRequest(BaseModel):
    age_group: str | None = None
    selected_party_id: UUID | None = None
    selected_party_status: Optional[Literal["none", "unknown", "skipped", "selected"]] = None
    interest_category_ids: list[str] = []

    @field_validator("age_group")
    @classmethod
    def validate_age_group(cls, v: str | None) -> str | None:
        if v is not None and v not in ALLOWED_AGE_GROUPS:
            raise ValueError(f"age_group must be one of {ALLOWED_AGE_GROUPS}")
        return v

    @field_validator("interest_category_ids")
    @classmethod
    def validate_interest_category_ids(cls, v: list[str]) -> list[str]:
        if len(v) > MAX_INTEREST_CATEGORY_IDS:
            raise ValueError(
                f"interest_category_ids must not exceed {MAX_INTEREST_CATEGORY_IDS}"
            )
        return v


class ArticleEventRequest(BaseModel):
    event_type: Literal["impression", "card_click", "detail_view", "helpful_click", "source_click"]
    article_id: UUID
    surface: Literal["home", "party_tab", "party_detail", "article_detail"]
