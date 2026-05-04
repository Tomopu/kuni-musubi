"""analytics API のリクエストバリデーションテスト。

実際の DB には接続せず、モックセッションを使って動作を確認する。
"""

import uuid

from fastapi.testclient import TestClient


class TestPostOnboardingEvent:
    """POST /analytics/onboarding のバリデーション。"""

    def test_valid_full_payload(self, client: TestClient) -> None:
        """有効なフルペイロードは 204 を返す。"""
        resp = client.post(
            "/analytics/onboarding",
            json={
                "age_group": "20s",
                "selected_party_id": str(uuid.uuid4()),
                "selected_party_status": "selected",
                "interest_category_ids": ["tax", "education"],
            },
        )
        assert resp.status_code == 204

    def test_valid_empty_payload(self, client: TestClient) -> None:
        """全フィールドが null / 空でも 204 を返す。"""
        resp = client.post(
            "/analytics/onboarding",
            json={},
        )
        assert resp.status_code == 204

    def test_invalid_age_group(self, client: TestClient) -> None:
        """許可されていない age_group は 422 を返す。"""
        resp = client.post(
            "/analytics/onboarding",
            json={"age_group": "999s"},
        )
        assert resp.status_code == 422

    def test_invalid_selected_party_status(self, client: TestClient) -> None:
        """許可されていない selected_party_status は 422 を返す。"""
        resp = client.post(
            "/analytics/onboarding",
            json={"selected_party_status": "invalid_status"},
        )
        assert resp.status_code == 422

    def test_too_many_interest_category_ids(self, client: TestClient) -> None:
        """interest_category_ids が 20 件超は 422 を返す。"""
        resp = client.post(
            "/analytics/onboarding",
            json={"interest_category_ids": [str(i) for i in range(21)]},
        )
        assert resp.status_code == 422

    def test_exactly_20_interest_category_ids(self, client: TestClient) -> None:
        """interest_category_ids が 20 件はギリギリ許可される。"""
        resp = client.post(
            "/analytics/onboarding",
            json={"interest_category_ids": [str(i) for i in range(20)]},
        )
        assert resp.status_code == 204


class TestPostArticleEvent:
    """POST /analytics/article-event のバリデーション。"""

    def test_valid_payload(self, client: TestClient) -> None:
        """有効なペイロードは 204 を返す。"""
        resp = client.post(
            "/analytics/article-event",
            json={
                "event_type": "card_click",
                "article_id": str(uuid.uuid4()),
                "surface": "home",
            },
        )
        assert resp.status_code == 204

    def test_invalid_event_type(self, client: TestClient) -> None:
        """許可されていない event_type は 422 を返す。"""
        resp = client.post(
            "/analytics/article-event",
            json={
                "event_type": "unknown_event",
                "article_id": str(uuid.uuid4()),
                "surface": "home",
            },
        )
        assert resp.status_code == 422

    def test_invalid_surface(self, client: TestClient) -> None:
        """許可されていない surface は 422 を返す。"""
        resp = client.post(
            "/analytics/article-event",
            json={
                "event_type": "card_click",
                "article_id": str(uuid.uuid4()),
                "surface": "invalid_surface",
            },
        )
        assert resp.status_code == 422

    def test_invalid_article_id(self, client: TestClient) -> None:
        """UUID でない article_id は 422 を返す。"""
        resp = client.post(
            "/analytics/article-event",
            json={
                "event_type": "card_click",
                "article_id": "not-a-uuid",
                "surface": "home",
            },
        )
        assert resp.status_code == 422

    def test_missing_required_field(self, client: TestClient) -> None:
        """必須フィールドがない場合は 422 を返す。"""
        resp = client.post(
            "/analytics/article-event",
            json={
                "event_type": "card_click",
                # article_id が欠如
                "surface": "home",
            },
        )
        assert resp.status_code == 422

    def test_all_event_types(self, client: TestClient) -> None:
        """すべての有効な event_type が 204 を返す。"""
        valid_types = [
            "impression",
            "card_click",
            "detail_view",
            "helpful_click",
            "source_click",
        ]
        for event_type in valid_types:
            resp = client.post(
                "/analytics/article-event",
                json={
                    "event_type": event_type,
                    "article_id": str(uuid.uuid4()),
                    "surface": "home",
                },
            )
            assert resp.status_code == 204, f"event_type={event_type} が失敗"

    def test_all_surfaces(self, client: TestClient) -> None:
        """すべての有効な surface が 204 を返す。"""
        valid_surfaces = ["home", "party_tab", "party_detail", "article_detail"]
        for surface in valid_surfaces:
            resp = client.post(
                "/analytics/article-event",
                json={
                    "event_type": "card_click",
                    "article_id": str(uuid.uuid4()),
                    "surface": surface,
                },
            )
            assert resp.status_code == 204, f"surface={surface} が失敗"
