from uuid import UUID

from pydantic import BaseModel


class PartyResponse(BaseModel):
    id: UUID
    name: str
    short_name: str


class PartyDetailResponse(PartyResponse):
    pass
