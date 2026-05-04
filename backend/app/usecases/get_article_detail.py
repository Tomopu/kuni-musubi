import json
from uuid import UUID

from sqlalchemy.orm import Session

from app.infrastructure.db.models import Article, ArticleDisplayContent
from app.infrastructure.db.repositories.article_repository import ArticleRepository
from app.schemas.article import (
    ArticleCategoryResponse,
    ArticleDetailResponse,
    ArticleDisplayContentResponse,
    ArticlePartyResponse,
    ArticleSourceResponse,
    ArticleThumbnail,
)


def execute(db: Session, *, article_id: UUID) -> ArticleDetailResponse | None:
    # 1. ArticleRepository から記事詳細を取得する
    repo = ArticleRepository(db)
    article = repo.get_by_id(article_id)
    if article is None:
        return None

    # 2. display_content を構築する
    dc: ArticleDisplayContent | None = article.display_content
    display_content = None
    if dc:
        # remaining_issues は JSON 配列文字列またはプレーンテキストとして保存されている
        remaining_issues: list[str]
        try:
            parsed = json.loads(dc.remaining_issues)
            if isinstance(parsed, list):
                remaining_issues = [str(item) for item in parsed]
            else:
                remaining_issues = [dc.remaining_issues]
        except (json.JSONDecodeError, TypeError):
            remaining_issues = [dc.remaining_issues] if dc.remaining_issues else []

        display_content = ArticleDisplayContentResponse(
            positive_point=dc.positive_point,
            life_impact=dc.life_impact,
            remaining_issues=remaining_issues,
            public_reactions_summary=dc.public_reactions_summary,
        )

    # 3. 出典をレスポンス形式に変換する
    sources = [
        ArticleSourceResponse(
            source_name=s.source_name,
            source_url=s.source_url,
            published_at=s.published_at,
            retrieved_at=s.retrieved_at,
        )
        for s in article.sources
    ]

    # 4. 関連政党をレスポンス形式に変換する
    parties = [
        ArticlePartyResponse(
            id=p.id,
            name=p.name,
            short_name=p.short_name,
            color_hex=p.color_hex or "#999999",
        )
        for p in article.parties
    ]

    # 5. 関連カテゴリをレスポンス形式に変換する
    categories = [
        ArticleCategoryResponse(id=c.id, name=c.name)
        for c in article.categories
    ]

    thumbnail = ArticleThumbnail(
        type=dc.thumbnail_type or "none" if dc else "none",
        text=dc.thumbnail_text if dc else None,
        url=dc.thumbnail_url if dc else None,
    )

    return ArticleDetailResponse(
        id=article.id,
        display_title=dc.display_title if dc else "",
        card_summary=dc.card_summary if dc else "",
        thumbnail=thumbnail,
        parties=parties,
        categories=categories,
        published_at=article.published_at,
        display_content=display_content,
        sources=sources,
    )
