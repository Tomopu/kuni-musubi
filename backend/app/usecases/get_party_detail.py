from uuid import UUID

from sqlalchemy.orm import Session

from app.schemas.party import PartyDetailResponse


def execute(db: Session, *, party_id: UUID) -> PartyDetailResponse | None:
    return None
