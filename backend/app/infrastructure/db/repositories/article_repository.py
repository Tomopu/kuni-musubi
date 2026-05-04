# ArticleRepository: DB から記事データを取得する

from datetime import datetime
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.infrastructure.db.models import Article, article_categories, article_parties


class ArticleRepository:
    def __init__(self, db: Session):
        self.db = db

    def _parse_cursor(self, cursor: str) -> tuple[datetime, UUID] | None:
        # 1. "|" で分割して published_at と article_id を取得
        # 2. パースに失敗した場合は None を返す
        try:
            parts = cursor.split("|", 1)
            if len(parts) != 2:
                return None
            published_at = datetime.fromisoformat(parts[0])
            article_id = UUID(parts[1])
            return published_at, article_id
        except (ValueError, AttributeError):
            return None

    def list_articles(
        self,
        party_ids: list[UUID] | None = None,
        category_ids: list[UUID] | None = None,
        sort: str = "latest",  # "latest" がデフォルト値
        limit: int = 20,
        cursor: str | None = None,
    ) -> list[Article]:
        # 1. ベースクエリ（display_content、parties、categories と一緒に取得）
        stmt = (
            select(Article)
            .options(
                joinedload(Article.display_content),
                joinedload(Article.parties),
                joinedload(Article.categories),
            )
            .where(Article.is_published == True)
        )

        # 2. party_ids フィルタを適用（中間テーブルを使って絞り込む）
        if party_ids:
            stmt = stmt.where(
                Article.id.in_(
                    select(article_parties.c.article_id).where(
                        article_parties.c.party_id.in_(party_ids)
                    )
                )
            )

        # 3. category_ids フィルタを適用（中間テーブルを使って絞り込む）
        if category_ids:
            stmt = stmt.where(
                Article.id.in_(
                    select(article_categories.c.article_id).where(
                        article_categories.c.category_id.in_(category_ids)
                    )
                )
            )

        # 4. cursor が指定されている場合: (published_at < cursor_published_at) OR
        #    (published_at == cursor_published_at AND id < cursor_id) の条件を追加
        if cursor:
            parsed = self._parse_cursor(cursor)
            if parsed is not None:
                cursor_published_at, cursor_id = parsed
                if sort == "important":
                    # important ソート時は published_at DESC を補助キーとして使う
                    stmt = stmt.where(
                        or_(
                            Article.published_at < cursor_published_at,
                            (Article.published_at == cursor_published_at)
                            & (Article.id < cursor_id),
                        )
                    )
                else:
                    stmt = stmt.where(
                        or_(
                            Article.published_at < cursor_published_at,
                            (Article.published_at == cursor_published_at)
                            & (Article.id < cursor_id),
                        )
                    )

        # 5. sort 順を適用（important: important_rank ASC NULLS LAST, published_at DESC /
        #    latest: published_at DESC, id DESC）
        if sort == "important":
            stmt = stmt.order_by(
                Article.important_rank.asc().nullslast(),
                Article.published_at.desc(),
                Article.id.desc(),
            )
        else:
            stmt = stmt.order_by(
                Article.published_at.desc(),
                Article.id.desc(),
            )

        # 6. limit+1 件取得して次ページ有無を判断
        stmt = stmt.limit(limit + 1)

        return list(self.db.scalars(stmt).unique().all())

    def get_by_id(self, article_id: UUID) -> Article | None:
        # 1. 記事を display_content、sources、parties、categories と一緒に取得
        stmt = (
            select(Article)
            .options(
                joinedload(Article.display_content),
                joinedload(Article.sources),
                joinedload(Article.parties),
                joinedload(Article.categories),
            )
            .where(Article.id == article_id)
        )
        return self.db.scalars(stmt).unique().first()
