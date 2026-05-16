from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.infrastructure.db.session import get_db
from app.schemas.category import PolicyCategoryResponse
from app.usecases import list_policy_categories

router = APIRouter(prefix="/policy-categories", tags=["categories"])


@router.get("", response_model=list[PolicyCategoryResponse])
def get_policy_categories(
    db: Annotated[Session, Depends(get_db)],
) -> list[PolicyCategoryResponse]:
    return list_policy_categories.execute(db)
