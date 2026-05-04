from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.infrastructure.db.session import get_db
from app.schemas.party import PartyDetailResponse, PartyResponse
from app.usecases import get_party_detail, list_parties

router = APIRouter(prefix="/parties", tags=["parties"])


@router.get("", response_model=list[PartyResponse])
def get_parties(
    db: Annotated[Session, Depends(get_db)],
) -> list[PartyResponse]:
    return list_parties.execute(db)


@router.get("/{party_id}", response_model=PartyDetailResponse)
def get_party(
    party_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> PartyDetailResponse:
    party = get_party_detail.execute(db, party_id=party_id)
    if party is None:
        raise HTTPException(status_code=404, detail="Party not found")
    return party
