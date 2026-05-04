from sqlalchemy.orm import Session

from app.infrastructure.db.repositories.category_repository import CategoryRepository
from app.schemas.category import PolicyCategoryResponse


def execute(db: Session) -> list[PolicyCategoryResponse]:
    # 1. CategoryRepository からカテゴリ一覧を取得する
    repo = CategoryRepository(db)
    categories = repo.list_categories()

    # 2. レスポンス形式に変換して返す
    return [
        PolicyCategoryResponse(
            id=c.id,
            name=c.name,
            slug=c.slug,
            display_order=c.display_order,
        )
        for c in categories
    ]
