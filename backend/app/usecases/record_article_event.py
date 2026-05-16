from sqlalchemy import text
from sqlalchemy.orm import Session

from app.infrastructure.db.models import ArticleEvent
from app.schemas.analytics import ArticleEventRequest

STAT_COLUMN_BY_EVENT_TYPE = {
    "impression": "impression_count",
    "card_click": "card_click_count",
    "detail_view": "detail_view_count",
    "source_click": "source_click_count",
    "helpful_click": "helpful_click_count",
    "unhelpful_click": "unhelpful_click_count",
}


def execute(db: Session, *, payload: ArticleEventRequest) -> None:
    event = ArticleEvent(
        event_type=payload.event_type,
        article_id=payload.article_id,
        surface=payload.surface,
    )
    db.add(event)
    stat_column = STAT_COLUMN_BY_EVENT_TYPE.get(payload.event_type)
    if stat_column:
        db.execute(
            text(
                f"""
                INSERT INTO daily_article_stats (
                    article_id,
                    stat_date,
                    {stat_column},
                    created_at,
                    updated_at
                )
                VALUES (:article_id, CURRENT_DATE, 1, now(), now())
                ON CONFLICT (article_id, stat_date)
                DO UPDATE SET
                    {stat_column} = daily_article_stats.{stat_column} + 1,
                    updated_at = now()
                """
            ),
            {"article_id": payload.article_id},
        )
    db.commit()
