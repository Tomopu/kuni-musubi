import os
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.infrastructure.db.dev_schema import ensure_dev_schema
from app.infrastructure.db.session import engine
from app.infrastructure.db.session import get_db
from app.schemas.party import PartyDetailResponse, PartyResponse
from app.usecases import get_party_detail, list_parties

router = APIRouter(prefix="/parties", tags=["parties"])
_PARTY_SCHEMA_READY = False


def _ensure_party_schema_ready() -> None:
    """政党 API で使う追加カラムをローカル開発DBに反映する。"""
    global _PARTY_SCHEMA_READY
    if _PARTY_SCHEMA_READY:
        return
    if os.getenv("SKIP_DB_INIT", "").lower() in {"1", "true", "yes"}:
        _PARTY_SCHEMA_READY = True
        return
    ensure_dev_schema(engine)
    _PARTY_SCHEMA_READY = True


@router.get("", response_model=list[PartyResponse])
def get_parties(
    db: Annotated[Session, Depends(get_db)],
) -> list[PartyResponse]:
    _ensure_party_schema_ready()
    return list_parties.execute(db)


@router.get("/{party_id}", response_model=PartyDetailResponse)
def get_party(
    party_id: UUID,
    db: Annotated[Session, Depends(get_db)],
) -> PartyDetailResponse:
    _ensure_party_schema_ready()
    party = get_party_detail.execute(db, party_id=party_id)
    if party is None:
        raise HTTPException(status_code=404, detail="Party not found")
    return party
