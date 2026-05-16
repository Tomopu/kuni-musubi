# PartyRepository: DB から政党データを取得する

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.db.models import Party


class PartyRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_parties(self) -> list[Party]:
        # 1. is_active=True の政党を display_order ASC で取得
        stmt = (
            select(Party)
            .where(Party.is_active == True)
            .order_by(Party.display_order.asc())
        )
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, party_id: UUID) -> Party | None:
        # 1. ID で政党を取得
        stmt = select(Party).where(Party.id == party_id)
        return self.db.scalars(stmt).first()
