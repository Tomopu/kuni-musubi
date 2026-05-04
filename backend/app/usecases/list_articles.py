from uuid import UUID

from sqlalchemy.orm import Session

from app.infrastructure.db.models import Article, ArticleDisplayContent
from app.infrastructure.db.repositories.article_repository import ArticleRepository
from app.schemas.article import (
    ArticleCardResponse,
    ArticleCategoryResponse,
    ArticleListResponse,
    ArticlePartyResponse,
    ArticleThumbnail,
)

MAX_LIMIT = 50
DEFAULT_LIMIT = 20


def _build_card_response(article: Article) -> ArticleCardResponse:
    # 1. display_content から表示用データを取得する
    dc: ArticleDisplayContent | None = article.display_content

    thumbnail = ArticleThumbnail(
        type=dc.thumbnail_type or "none" if dc else "none",
        text=dc.thumbnail_text if dc else None,
        url=dc.thumbnail_url if dc else None,
    )

    # 2. 関連政党をレスポンス形式に変換する
    parties = [
        ArticlePartyResponse(
            id=p.id,
            name=p.name,
            short_name=p.short_name,
            color_hex=p.color_hex or "#999999",
        )
        for p in article.parties
    ]

    # 3. 関連カテゴリをレスポンス形式に変換する
    categories = [
        ArticleCategoryResponse(id=c.id, name=c.name)
        for c in article.categories
    ]

    return ArticleCardResponse(
        id=article.id,
        display_title=dc.display_title if dc else "",
        card_summary=dc.card_summary if dc else "",
        thumbnail=thumbnail,
        parties=parties,
        categories=categories,
        published_at=article.published_at,
    )


def execute(
    db: Session,
    *,
    party_id: UUID | None,
    category_ids: list[str],
    sort: str = "latest",
    limit: int,
    cursor: str | None,
) -> ArticleListResponse:
    # 1. 入力値を正規化する
    effective_limit = min(limit, MAX_LIMIT)
    party_ids = [party_id] if party_id else None
    cat_uuids = [UUID(cid) for cid in category_ids if cid] if category_ids else None

    # 2. ArticleRepository から記事一覧を取得する
    repo = ArticleRepository(db)
    articles = repo.list_articles(
        party_ids=party_ids,
        category_ids=cat_uuids,
        sort=sort,
        limit=effective_limit,
        cursor=cursor,
    )

    # 3. limit+1 件取得した結果で next_cursor を判断する
    has_next = len(articles) > effective_limit
    items = articles[:effective_limit]
    # next_cursor は "{published_at_iso}|{article_id}" 形式で返す
    next_cursor = (
        f"{items[-1].published_at.isoformat()}|{items[-1].id}"
        if has_next and items
        else None
    )

    # 4. 記事カードレスポンスのリストを構築して返す
    return ArticleListResponse(
        items=[_build_card_response(a) for a in items],
        next_cursor=next_cursor,
    )
