"""セーフティーガードのユニットテスト。

DomainRateLimiter、compute_backoff_seconds、check_robots_txt の動作を検証する。
"""

import time
from unittest.mock import MagicMock, patch
from urllib.robotparser import RobotFileParser

import pytest

from batch.scrapers.safety import DomainRateLimiter, check_robots_txt, compute_backoff_seconds


class TestComputeBackoffSeconds:
    """compute_backoff_seconds の計算ロジックのテスト。"""

    def test_attempt_0_returns_base(self) -> None:
        assert compute_backoff_seconds(0, base=1.0, factor=2.0) == pytest.approx(1.0)

    def test_attempt_1_returns_base_times_factor(self) -> None:
        assert compute_backoff_seconds(1, base=1.0, factor=2.0) == pytest.approx(2.0)

    def test_attempt_2_returns_base_times_factor_squared(self) -> None:
        assert compute_backoff_seconds(2, base=1.0, factor=2.0) == pytest.approx(4.0)

    def test_custom_base_and_factor(self) -> None:
        # base=3.0, factor=3.0, attempt=1 → 3.0 * 3.0^1 = 9.0
        assert compute_backoff_seconds(1, base=3.0, factor=3.0) == pytest.approx(9.0)


class TestDomainRateLimiter:
    """DomainRateLimiter のレートリミット動作のテスト。"""

    def test_first_access_does_not_wait(self) -> None:
        """初回アクセスは待機なしで即時返る。"""
        limiter = DomainRateLimiter(interval_seconds=5.0)
        start = time.monotonic()
        limiter.wait_if_needed("https://example.com/feed")
        elapsed = time.monotonic() - start
        # 初回は前回アクセスがないため待機なし（0.5秒以内）
        assert elapsed < 0.5

    def test_second_access_same_domain_waits(self) -> None:
        """同一ドメインへの連続アクセスは interval_seconds 待機する。"""
        interval = 0.2  # テスト用に短い間隔を設定
        limiter = DomainRateLimiter(interval_seconds=interval)
        limiter.wait_if_needed("https://example.com/feed")

        start = time.monotonic()
        limiter.wait_if_needed("https://example.com/other")
        elapsed = time.monotonic() - start
        # interval 秒以上待機していることを確認（バッファ 0.05 秒）
        assert elapsed >= interval - 0.05

    def test_different_domains_do_not_interfere(self) -> None:
        """異なるドメインはそれぞれ独立してレートリミットが適用される。"""
        interval = 0.3
        limiter = DomainRateLimiter(interval_seconds=interval)
        limiter.wait_if_needed("https://example.com/feed")

        start = time.monotonic()
        limiter.wait_if_needed("https://other.example.org/rss")
        elapsed = time.monotonic() - start
        # 異なるドメインなので待機なし（0.5秒以内）
        assert elapsed < 0.5

    def test_sufficient_elapsed_time_does_not_wait(self) -> None:
        """前回アクセスから interval 以上経過していれば待機しない。"""
        interval = 0.1
        limiter = DomainRateLimiter(interval_seconds=interval)
        limiter.wait_if_needed("https://example.com/feed")
        time.sleep(interval + 0.05)  # interval を十分に超えて待機

        start = time.monotonic()
        limiter.wait_if_needed("https://example.com/feed")
        elapsed = time.monotonic() - start
        assert elapsed < 0.15  # 追加待機なし


class TestCheckRobotsTxt:
    """check_robots_txt の robots.txt 解釈テスト。"""

    def test_allows_access_when_robots_permits(self) -> None:
        """robots.txt がアクセスを許可している場合は True を返す。"""
        mock_rp = MagicMock(spec=RobotFileParser)
        mock_rp.can_fetch.return_value = True

        with patch("batch.scrapers.safety.RobotFileParser", return_value=mock_rp):
            result = check_robots_txt("https://example.com/rss", user_agent="TestBot")

        assert result is True
        mock_rp.read.assert_called_once()
        mock_rp.can_fetch.assert_called_once_with("TestBot", "https://example.com/rss")

    def test_denies_access_when_robots_disallows(self) -> None:
        """robots.txt がアクセスを禁止している場合は False を返す。"""
        mock_rp = MagicMock(spec=RobotFileParser)
        mock_rp.can_fetch.return_value = False

        with patch("batch.scrapers.safety.RobotFileParser", return_value=mock_rp):
            result = check_robots_txt("https://example.com/rss", user_agent="TestBot")

        assert result is False

    def test_returns_true_when_robots_fetch_fails(self) -> None:
        """robots.txt の取得に失敗した場合はフェイルオープンで True を返す。"""
        mock_rp = MagicMock(spec=RobotFileParser)
        mock_rp.read.side_effect = OSError("Connection refused")

        with patch("batch.scrapers.safety.RobotFileParser", return_value=mock_rp):
            result = check_robots_txt("https://unreachable.example.com/rss")

        assert result is True

    def test_robots_url_is_built_from_feed_url(self) -> None:
        """robots.txt の URL がフィード URL のルートドメインから生成されることを確認する。"""
        mock_rp = MagicMock(spec=RobotFileParser)
        mock_rp.can_fetch.return_value = True

        with patch("batch.scrapers.safety.RobotFileParser", return_value=mock_rp):
            check_robots_txt("https://www.example.co.jp/news/rss.xml")

        mock_rp.set_url.assert_called_once_with("https://www.example.co.jp/robots.txt")


class TestGetWithRetry:
    """_get_with_retry のリトライ・バックオフ動作のテスト。"""

    def test_retries_on_non_abort_http_error(self) -> None:
        """429/503 以外の HTTP エラーでは指定回数リトライする。"""
        import httpx

        from batch.scrapers.rss import _get_with_retry

        mock_request = MagicMock()
        mock_response_500 = MagicMock(spec=httpx.Response)
        mock_response_500.status_code = 500

        call_count = 0

        def fake_get(url: str, headers: dict) -> httpx.Response:  # type: ignore[return]
            nonlocal call_count
            call_count += 1
            raise httpx.HTTPStatusError(
                "500 error", request=mock_request, response=mock_response_500
            )

        mock_client = MagicMock(spec=httpx.Client)
        mock_client.get.side_effect = fake_get

        with (
            patch("batch.scrapers.rss.check_robots_txt", return_value=True),
            patch("batch.scrapers.rss.domain_rate_limiter") as mock_limiter,
            patch("batch.scrapers.rss.settings") as mock_settings,
            patch("batch.scrapers.rss.time.sleep"),
        ):
            mock_limiter.wait_if_needed = MagicMock()
            mock_settings.scraper_max_retries = 1
            mock_settings.scraper_request_delay_seconds = 0.01
            mock_settings.scraper_backoff_factor = 2.0

            with pytest.raises(httpx.HTTPStatusError):
                _get_with_retry(mock_client, "https://example.com/rss")

        # 初回 + 1回リトライ = 計2回
        assert call_count == 2

    def test_aborts_immediately_on_429(self) -> None:
        """429 エラーは即時停止してリトライしない。"""
        import httpx

        from batch.scrapers.rss import _get_with_retry

        mock_request = MagicMock()
        mock_response_429 = MagicMock(spec=httpx.Response)
        mock_response_429.status_code = 429

        call_count = 0

        def fake_get(url: str, headers: dict) -> httpx.Response:  # type: ignore[return]
            nonlocal call_count
            call_count += 1
            raise httpx.HTTPStatusError(
                "429 Too Many Requests", request=mock_request, response=mock_response_429
            )

        mock_client = MagicMock(spec=httpx.Client)
        mock_client.get.side_effect = fake_get

        with (
            patch("batch.scrapers.rss.check_robots_txt", return_value=True),
            patch("batch.scrapers.rss.domain_rate_limiter") as mock_limiter,
            patch("batch.scrapers.rss.settings") as mock_settings,
            patch("batch.scrapers.rss.time.sleep"),
        ):
            mock_limiter.wait_if_needed = MagicMock()
            mock_settings.scraper_max_retries = 2
            mock_settings.scraper_request_delay_seconds = 0.01
            mock_settings.scraper_backoff_factor = 2.0

            with pytest.raises(httpx.HTTPStatusError):
                _get_with_retry(mock_client, "https://example.com/rss")

        # 429 は即時停止のためリトライなしで1回のみ
        assert call_count == 1

    def test_raises_permission_error_when_robots_disallows(self) -> None:
        """robots.txt でアクセス禁止の場合は PermissionError を送出する。"""
        import httpx

        from batch.scrapers.rss import _get_with_retry

        mock_client = MagicMock(spec=httpx.Client)

        with patch("batch.scrapers.rss.check_robots_txt", return_value=False):
            with pytest.raises(PermissionError, match="robots.txt"):
                _get_with_retry(mock_client, "https://example.com/rss")

        mock_client.get.assert_not_called()
