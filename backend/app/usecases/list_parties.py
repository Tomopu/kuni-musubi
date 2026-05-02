from sqlalchemy.orm import Session

from app.schemas.party import PartyResponse


def execute(db: Session) -> list[PartyResponse]:
    return []
