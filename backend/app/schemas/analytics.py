from typing import Literal
from uuid import UUID

from pydantic import BaseModel

ALLOWED_EVENT_TYPES = {
    "impression",
    "card_click",
    "detail_view",
    "helpful_click",
    "unhelpful_click",
    "source_click",
}
ALLOWED_SURFACES = {"home", "party_tab", "party_detail", "article_detail"}


class ArticleEventRequest(BaseModel):
    event_type: Literal[
        "impression",
        "card_click",
        "detail_view",
        "helpful_click",
        "unhelpful_click",
        "source_click",
    ]
    article_id: UUID
    surface: Literal["home", "party_tab", "party_detail", "article_detail"]
