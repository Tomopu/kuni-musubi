from uuid import UUID

from sqlalchemy.orm import Session

from app.infrastructure.db.models import Party


def find_by_id(db: Session, party_id: UUID) -> Party | None:
    return db.query(Party).filter(Party.id == party_id).first()


def find_all(db: Session) -> list[Party]:
    return db.query(Party).order_by(Party.name).all()
