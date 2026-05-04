from uuid import UUID

from pydantic import BaseModel


class PolicyCategoryResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    display_order: int = 0
