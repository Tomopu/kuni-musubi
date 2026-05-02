from sqlalchemy.orm import Session

from app.infrastructure.db.models import OnboardingEvent
from app.schemas.analytics import OnboardingEventRequest


def execute(db: Session, *, payload: OnboardingEventRequest) -> None:
    event = OnboardingEvent(
        age_group=payload.age_group,
        selected_party_id=payload.selected_party_id,
        interest_category_ids=payload.interest_category_ids,
    )
    db.add(event)
    db.commit()
