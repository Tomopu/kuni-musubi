"""Pydantic スキーマのユニットテスト（DB 不要）。"""

import pytest
from pydantic import ValidationError

from app.schemas.analytics import (
    ArticleEventRequest,
)


class TestArticleEventRequest:
    def test_valid_payload(self) -> None:
        """有効なペイロードは検証を通過する。"""
        import uuid

        req = ArticleEventRequest(
            event_type="card_click",
            article_id=uuid.uuid4(),
            surface="home",
        )
        assert req.event_type == "card_click"
        assert req.surface == "home"

    def test_invalid_event_type(self) -> None:
        """不正な event_type は ValidationError。"""
        import uuid

        with pytest.raises(ValidationError):
            ArticleEventRequest(
                event_type="unknown",
                article_id=uuid.uuid4(),
                surface="home",
            )

    def test_invalid_surface(self) -> None:
        """不正な surface は ValidationError。"""
        import uuid

        with pytest.raises(ValidationError):
            ArticleEventRequest(
                event_type="card_click",
                article_id=uuid.uuid4(),
                surface="invalid_surface",
            )
