from sqlalchemy.orm import Session

from app.schemas.category import PolicyCategoryResponse


def execute(db: Session) -> list[PolicyCategoryResponse]:
    return []
