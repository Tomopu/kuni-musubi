"""DB 保存ステップ。

ArticleLLMOutput を articles / article_display_contents / article_sources /
article_parties / article_categories テーブルに保存する。

依存: backend の ORM モデルを共用するため、実行時に PYTHONPATH=../backend が必要。
  例: PYTHONPATH=../backend uv run python -m batch.main
"""

import json
import uuid
from datetime import datetime, timezone

# backend の ORM モデルを共用する（PYTHONPATH=../backend が必要）
from app.infrastructure.db.models import (
    Article,
    ArticleDisplayContent,
    ArticleSource,
    Party,
    PolicyCategory,
    article_categories,
    article_parties,
)
from sqlalchemy.orm import Session

from batch.llm.schemas.article import ArticleLLMOutput
from batch.steps.fetch import FetchResult


def _resolve_party_id(session: Session, party_name: str) -> uuid.UUID | None:
    """政党名から parties テーブルの id を引く（完全一致のみ）。

    部分一致は誤紐付けリスクがあるため使用しない。
    """
    # 1. name 完全一致
    party = session.query(Party).filter(Party.name == party_name).first()
    if party:
        return party.id
    # 2. short_name 完全一致
    party = session.query(Party).filter(Party.short_name == party_name).first()
    return party.id if party else None


def _resolve_category_id(session: Session, category_name: str) -> uuid.UUID | None:
    """カテゴリ名から policy_categories テーブルの id を引く（完全一致のみ）。"""
    cat = (
        session.query(PolicyCategory)
        .filter(PolicyCategory.name == category_name)
        .first()
    )
    return cat.id if cat else None


def save_article(
    session: Session,
    fetch_result: FetchResult,
    llm_output: ArticleLLMOutput,
) -> uuid.UUID:
    """LLM 処理結果を DB に保存し、作成した article_id を返す。

    1. articles レコードを作成する
    2. article_display_contents レコードを作成する
    3. article_sources レコードを作成する
    4. article_parties 中間レコードを作成する
    5. article_categories 中間レコードを作成する
    """
    # 1. articles を作成する
    needs_human_review = llm_output.quality_flags.needs_human_review
    article = Article(
        id=uuid.uuid4(),
        original_title=fetch_result.title,
        source_type=fetch_result.source_type,
        primary_source_url=fetch_result.source_url,
        published_at=_parse_published_at(fetch_result.published_at),
        collected_at=datetime.now(tz=timezone.utc),
        status="processed" if not needs_human_review else "draft",
        is_published=not needs_human_review,
    )
    session.add(article)
    session.flush()  # article.id を確定させる

    # 2. article_display_contents を作成する
    display_content = ArticleDisplayContent(
        id=uuid.uuid4(),
        article_id=article.id,
        display_title=llm_output.display_title,
        card_summary=llm_output.card_summary,
        positive_point=llm_output.positive_point,
        life_impact=llm_output.life_impact,
        remaining_issues=json.dumps(llm_output.remaining_issues, ensure_ascii=False),
        public_reactions_summary=json.dumps(
            llm_output.public_reactions_summary.model_dump(), ensure_ascii=False
        ),
        created_by="llm_batch",
    )
    session.add(display_content)

    # 3. article_sources を作成する
    source = ArticleSource(
        id=uuid.uuid4(),
        article_id=article.id,
        source_name=llm_output.source_summary.source_name or fetch_result.source_name,
        source_url=llm_output.source_summary.primary_source_url,
        source_type=llm_output.source_summary.source_type,
        published_at=_parse_published_at(llm_output.source_summary.published_at),
        retrieved_at=datetime.now(tz=timezone.utc),
    )
    session.add(source)

    # 4. article_parties 中間レコードを作成する
    for related in llm_output.related_parties:
        party_id = _resolve_party_id(session, related.party_name)
        if party_id is None:
            # 名寄せできない政党はスキップ（誤紐付けより未紐付けの方が安全）
            continue
        session.execute(
            article_parties.insert().values(
                article_id=article.id,
                party_id=party_id,
                relation_type=related.relation_type,
            )
        )

    # 5. article_categories 中間レコードを作成する
    for order, cat_name in enumerate(llm_output.categories):
        cat_id = _resolve_category_id(session, cat_name)
        if cat_id is None:
            continue
        session.execute(
            article_categories.insert().values(
                article_id=article.id,
                category_id=cat_id,
                display_order=order,
            )
        )

    return article.id


def _parse_published_at(date_str: str) -> datetime:
    """ISO 8601 文字列を datetime に変換する。失敗時は現在時刻を返す。"""
    if not date_str:
        return datetime.now(tz=timezone.utc)
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return datetime.now(tz=timezone.utc)
