"""import job / import_service のテスト。"""

import uuid
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


class TestGetActiveJob:
    """get_active_job のテスト。"""

    def test_returns_none_when_no_active_job(self) -> None:
        """実行中ジョブがない場合は None を返す。"""
        from app.api.admin.import_service import get_active_job

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = get_active_job(mock_db)
        assert result is None

    def test_returns_job_when_running(self) -> None:
        """running ジョブがある場合はそのジョブを返す。"""
        from app.api.admin.import_service import get_active_job

        mock_job = MagicMock()
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_job
        result = get_active_job(mock_db)
        assert result is mock_job


class TestHasGeminiKey:
    """has_gemini_key のテスト。"""

    def test_returns_true_when_key_set(self) -> None:
        from app.api.admin.import_service import has_gemini_key
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            assert has_gemini_key() is True

    def test_returns_false_when_key_empty(self) -> None:
        from app.api.admin.import_service import has_gemini_key
        with patch.dict("os.environ", {"GEMINI_API_KEY": ""}, clear=False):
            # GEMINI_API_KEY を空文字で上書き
            import os
            original = os.environ.pop("GEMINI_API_KEY", None)
            try:
                assert has_gemini_key() is False
            finally:
                if original is not None:
                    os.environ["GEMINI_API_KEY"] = original


class TestImportsRunRoute:
    """POST /admin/imports/run の統合テスト（モック DB）。"""

    def test_rejects_when_active_job_exists(self, client: TestClient) -> None:
        """実行中ジョブがある場合は新規ジョブを拒否してリダイレクトする。"""
        with (
            patch("app.api.admin.router.get_current_admin") as mock_auth,
            patch("app.api.admin.router.get_active_job") as mock_active,
            patch("app.api.admin.router.has_gemini_key", return_value=True),
        ):
            mock_auth.return_value = MagicMock()
            mock_active.return_value = MagicMock()  # 実行中ジョブあり

            resp = client.post(
                "/admin/imports/run",
                data={"job_type": "full"},
                follow_redirects=False,
            )

        assert resp.status_code == 302
        assert "error" in resp.headers["location"]

    def test_rejects_when_no_gemini_key(self, client: TestClient) -> None:
        """Gemini キー未設定時は fetch_only 以外のジョブを拒否する。"""
        with (
            patch("app.api.admin.router.get_current_admin") as mock_auth,
            patch("app.api.admin.router.get_active_job", return_value=None),
            patch("app.api.admin.router.has_gemini_key", return_value=False),
        ):
            mock_auth.return_value = MagicMock()

            resp = client.post(
                "/admin/imports/run",
                data={"job_type": "full"},
                follow_redirects=False,
            )

        assert resp.status_code == 302
        assert "error" in resp.headers["location"]

    def test_fetch_only_allowed_without_gemini_key(self, client: TestClient) -> None:
        """fetch_only は Gemini キー不要で実行できる。"""
        with (
            patch("app.api.admin.router.get_current_admin") as mock_auth,
            patch("app.api.admin.router.get_active_job", return_value=None),
            patch("app.api.admin.router.has_gemini_key", return_value=False),
            patch("app.api.admin.router.create_and_start_job") as mock_create,
        ):
            mock_auth.return_value = MagicMock()
            mock_create.return_value = uuid.uuid4()

            resp = client.post(
                "/admin/imports/run",
                data={"job_type": "fetch_only"},
                follow_redirects=False,
            )

        assert resp.status_code == 302
        mock_create.assert_called_once()
        params = mock_create.call_args[0][0]
        assert params.fetch_only is True


class TestBulkArticleAction:
    """POST /admin/articles/bulk-action のテスト。"""

    def test_rejects_empty_selection(self, client: TestClient) -> None:
        """記事が選択されていない場合はエラーリダイレクト。"""
        with patch("app.api.admin.router.get_current_admin") as mock_auth:
            mock_auth.return_value = MagicMock()
            resp = client.post(
                "/admin/articles/bulk-action",
                data={"action": "publish"},
                follow_redirects=False,
            )
        assert resp.status_code == 302
        assert "error" in resp.headers["location"]

    def test_rejects_invalid_action(self, client: TestClient) -> None:
        """不正なアクション名はエラーリダイレクト。"""
        with patch("app.api.admin.router.get_current_admin") as mock_auth:
            mock_auth.return_value = MagicMock()
            resp = client.post(
                "/admin/articles/bulk-action",
                data={"action": "delete_all", "article_ids": [str(uuid.uuid4())]},
                follow_redirects=False,
            )
        assert resp.status_code == 302
        assert "error" in resp.headers["location"]

    def test_publish_updates_articles(self, client: TestClient) -> None:
        """publish アクションで is_published=True, status=published になる。"""
        article_id = uuid.uuid4()
        mock_article = MagicMock()
        mock_article.id = article_id

        with (
            patch("app.api.admin.router.get_current_admin") as mock_auth,
        ):
            mock_auth.return_value = MagicMock()
            # mock DB を使って article を返す
            from app.infrastructure.db.session import get_db
            from app.main import app

            mock_session = MagicMock()
            mock_session.query.return_value.filter.return_value.first.return_value = (
                mock_article
            )

            def _mock_db():
                yield mock_session

            app.dependency_overrides[get_db] = _mock_db
            try:
                resp = client.post(
                    "/admin/articles/bulk-action",
                    data={"action": "publish", "article_ids": [str(article_id)]},
                    follow_redirects=False,
                )
            finally:
                app.dependency_overrides.pop(get_db, None)

        assert resp.status_code == 302
        assert mock_article.is_published is True
        assert mock_article.status == "published"

    def test_unpublish_updates_articles(self, client: TestClient) -> None:
        """unpublish アクションで is_published=False, status=draft になる。"""
        article_id = uuid.uuid4()
        mock_article = MagicMock()
        mock_article.id = article_id

        with patch("app.api.admin.router.get_current_admin") as mock_auth:
            mock_auth.return_value = MagicMock()
            from app.infrastructure.db.session import get_db
            from app.main import app

            mock_session = MagicMock()
            mock_session.query.return_value.filter.return_value.first.return_value = (
                mock_article
            )

            def _mock_db():
                yield mock_session

            app.dependency_overrides[get_db] = _mock_db
            try:
                resp = client.post(
                    "/admin/articles/bulk-action",
                    data={"action": "unpublish", "article_ids": [str(article_id)]},
                    follow_redirects=False,
                )
            finally:
                app.dependency_overrides.pop(get_db, None)

        assert resp.status_code == 302
        assert mock_article.is_published is False
        assert mock_article.status == "draft"
