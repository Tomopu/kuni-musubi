from sqlalchemy.orm import Session

from app.infrastructure.db.repositories.party_repository import PartyRepository
from app.schemas.party import PartyResponse
from app.usecases.party_field_utils import normalize_text_list


def execute(db: Session) -> list[PartyResponse]:
    # 1. PartyRepository から政党一覧を取得する
    repo = PartyRepository(db)
    parties = repo.list_parties()

    # 2. レスポンス形式に変換して返す
    response: list[PartyResponse] = []
    for p in parties:
        main_policy_tags = normalize_text_list(p.main_policy_tags)
        main_policy_categories = normalize_text_list(p.main_policy_categories)
        response.append(
            PartyResponse(
                id=p.id,
                name=p.name,
                short_name=p.short_name,
                color_hex=p.color_hex,
                house_of_representatives_seats=p.house_of_representatives_seats,
                house_of_councillors_seats=p.house_of_councillors_seats,
                total_seats=(p.house_of_representatives_seats or 0)
                + (p.house_of_councillors_seats or 0),
                main_policy_tags=main_policy_tags,
                main_policy_categories=main_policy_categories or main_policy_tags,
            )
        )
    return response
