"""Pydantic スキーマのユニットテスト（DB 不要）。"""

import pytest
from pydantic import ValidationError

from app.schemas.analytics import (
    ALLOWED_AGE_GROUPS,
    ArticleEventRequest,
    OnboardingEventRequest,
)


class TestOnboardingEventRequest:
    def test_valid_all_fields(self) -> None:
        """すべてのフィールドが有効な場合は検証を通過する。"""
        import uuid

        req = OnboardingEventRequest(
            age_group="20s",
            selected_party_id=uuid.uuid4(),
            selected_party_status="selected",
            interest_category_ids=["cat1", "cat2"],
        )
        assert req.age_group == "20s"
        assert req.selected_party_status == "selected"

    def test_all_age_groups_are_valid(self) -> None:
        """ALLOWED_AGE_GROUPS に定義されたすべての値が通過する。"""
        for ag in ALLOWED_AGE_GROUPS:
            req = OnboardingEventRequest(age_group=ag)
            assert req.age_group == ag

    def test_none_age_group(self) -> None:
        """age_group=None は通過する。"""
        req = OnboardingEventRequest(age_group=None)
        assert req.age_group is None

    def test_invalid_age_group_raises(self) -> None:
        """不正な age_group は ValidationError になる。"""
        with pytest.raises(ValidationError):
            OnboardingEventRequest(age_group="999s")

    def test_interest_category_ids_limit(self) -> None:
        """interest_category_ids が 20 件超は ValidationError。"""
        with pytest.raises(ValidationError):
            OnboardingEventRequest(interest_category_ids=[str(i) for i in range(21)])

    def test_interest_category_ids_exactly_20(self) -> None:
        """interest_category_ids が 20 件は通過する。"""
        req = OnboardingEventRequest(interest_category_ids=[str(i) for i in range(20)])
        assert len(req.interest_category_ids) == 20


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
