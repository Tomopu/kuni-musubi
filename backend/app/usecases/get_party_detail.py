from uuid import UUID

from sqlalchemy.orm import Session

from app.infrastructure.db.repositories.article_repository import ArticleRepository
from app.infrastructure.db.repositories.party_repository import PartyRepository
from app.schemas.article import (
    ArticleCardResponse,
    ArticleCategoryResponse,
    ArticlePartyResponse,
    ArticleThumbnail,
)
from app.schemas.party import PartyDetailResponse
from app.usecases.party_field_utils import normalize_text_list

LATEST_ARTICLES_LIMIT = 3


def execute(db: Session, *, party_id: UUID) -> PartyDetailResponse | None:
    # 1. PartyRepository から政党詳細を取得する
    party_repo = PartyRepository(db)
    party = party_repo.get_by_id(party_id)
    if party is None:
        return None

    # 2. ArticleRepository からこの政党の最新記事3件を取得する
    article_repo = ArticleRepository(db)
    articles = article_repo.list_articles(
        party_ids=[party_id],
        sort="latest",
        limit=LATEST_ARTICLES_LIMIT,
    )
    items = articles[:LATEST_ARTICLES_LIMIT]

    # 3. 最新記事をカードレスポンス形式に変換する
    latest_articles: list[ArticleCardResponse] = []
    for a in items:
        dc = a.display_content
        thumbnail = ArticleThumbnail(
            type=dc.thumbnail_type or "none" if dc else "none",
            text=dc.thumbnail_text if dc else None,
            url=dc.thumbnail_url if dc else None,
        )
        article_parties = [
            ArticlePartyResponse(
                id=p.id,
                name=p.name,
                short_name=p.short_name,
                color_hex=p.color_hex or "#999999",
            )
            for p in a.parties
        ]
        article_categories = [
            ArticleCategoryResponse(id=c.id, name=c.name)
            for c in a.categories
        ]
        latest_articles.append(
            ArticleCardResponse(
                id=a.id,
                display_title=dc.display_title if dc else "",
                card_summary=dc.card_summary if dc else "",
                thumbnail=thumbnail,
                parties=article_parties,
                categories=article_categories,
                published_at=a.published_at,
            )
        )

    # 4. PartyDetailResponse を構築して返す
    manifesto_promises = normalize_text_list(party.manifesto_promises)
    policy_pillars = normalize_text_list(party.policy_pillars)
    main_policy_tags = normalize_text_list(party.main_policy_tags)
    main_policy_categories = normalize_text_list(party.main_policy_categories)
    return PartyDetailResponse(
        id=party.id,
        name=party.name,
        short_name=party.short_name,
        color_hex=party.color_hex,
        house_of_representatives_seats=party.house_of_representatives_seats,
        house_of_councillors_seats=party.house_of_councillors_seats,
        total_seats=(party.house_of_representatives_seats or 0)
        + (party.house_of_councillors_seats or 0),
        founded_year=party.founded_year,
        leader_name=party.leader_name,
        ideology_summary=party.ideology_summary,
        manifesto_summary=party.manifesto_summary,
        manifesto_promises=manifesto_promises,
        policy_headline=party.policy_headline,
        policy_headline_type=party.policy_headline_type,
        policy_pillars=policy_pillars,
        main_policy_tags=main_policy_tags,
        policy_source_type=party.policy_source_type,
        policy_source_label=party.policy_source_label,
        policy_source_url=party.policy_source_url,
        policy_last_checked=party.policy_last_checked,
        policy_note=party.policy_note,
        main_policy_categories=main_policy_categories or main_policy_tags,
        official_url=party.official_url,
        latest_articles=latest_articles,
    )
