# CategoryRepository: DB からカテゴリデータを取得する

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.db.models import PolicyCategory


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_categories(self) -> list[PolicyCategory]:
        # 1. カテゴリを display_order ASC で全件取得
        stmt = select(PolicyCategory).order_by(PolicyCategory.display_order.asc())
        return list(self.db.scalars(stmt).all())
