"""RSS フィード取得スクレイパー。"""

import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html import unescape
from typing import Any

import httpx
from bs4 import BeautifulSoup

from batch.scrapers.safety import check_robots_txt, compute_backoff_seconds, domain_rate_limiter
from batch.settings import settings

_USER_AGENT = "Kuni-Musubi-Bot/1.0"

# 即時停止する HTTP エラーコード（リトライしても無意味なため）
# 4xx: クライアント起因のエラー（URL 誤り・アクセス禁止など）はリトライしない
# 429: Too Many Requests, 503: Service Unavailable も即時停止
_ABORT_STATUS_CODES = {400, 401, 403, 404, 405, 410, 429, 503}


@dataclass
class RssItem:
    """RSS フィードの 1 件分のデータ。"""

    title: str
    url: str
    published_at: datetime
    source_name: str
    source_type: str = "news_media"
    body_text: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


def _parse_datetime(date_str: str) -> datetime:
    """RSS の日時文字列を datetime に変換する。失敗時は現在時刻を返す。"""
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S GMT",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return datetime.now(tz=timezone.utc)


def _strip_html(html_text: str) -> str:
    """HTML タグを除去してプレーンテキストを返す。"""
    soup = BeautifulSoup(html_text, "html.parser")
    text = soup.get_text(separator="\n")
    # 連続する空白行を 1 行に圧縮する
    text = re.sub(r"\n{3,}", "\n\n", text)
    return unescape(text).strip()


def _get_with_retry(client: httpx.Client, url: str) -> httpx.Response:
    """指数バックオフ付きリトライで HTTP GET を実行する。

    1. robots.txt を確認してアクセス可否を判定する
    2. ドメインレートリミッターで待機する
    3. GET リクエストを送信する
    4. 429/503 エラーは即時スキップする
    5. その他エラーは最大 SCRAPER_MAX_RETRIES 回リトライする
    """
    if not check_robots_txt(url):
        raise PermissionError(f"robots.txt によりアクセス禁止: {url}")

    last_exc: Exception = RuntimeError("未到達")
    for attempt in range(settings.scraper_max_retries + 1):
        if attempt > 0:
            wait = compute_backoff_seconds(
                attempt - 1,
                base=settings.scraper_request_delay_seconds,
                factor=settings.scraper_backoff_factor,
            )
            print(f"[rss] リトライ待機 {wait:.1f}s (attempt {attempt}): {url}")
            time.sleep(wait)

        # ドメインレートリミッター適用
        domain_rate_limiter.wait_if_needed(url)

        try:
            resp = client.get(url, headers={"User-Agent": _USER_AGENT})
            if resp.status_code in _ABORT_STATUS_CODES:
                raise httpx.HTTPStatusError(
                    f"即時停止 status={resp.status_code}",
                    request=resp.request,
                    response=resp,
                )
            resp.raise_for_status()
            # 成功後は次リクエストとの間隔を保証するため待機する
            time.sleep(settings.scraper_request_delay_seconds)
            return resp
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in _ABORT_STATUS_CODES:
                raise
            last_exc = exc
        except Exception as exc:
            last_exc = exc

    raise last_exc


def fetch_rss(
    feed_url: str,
    source_name: str,
    source_type: str = "news_media",
    max_items: int | None = None,
) -> list[RssItem]:
    """RSS フィードを取得してパースした結果を返す。

    1. セーフティーガードを通じて HTTP GET でフィードを取得する
    2. BeautifulSoup で item/entry 要素をパースする
    3. RssItem のリストとして返す
    """
    if max_items is None:
        max_items = settings.rss_max_items

    with httpx.Client(
        timeout=settings.scraper_timeout,
        follow_redirects=True,
    ) as client:
        resp = _get_with_retry(client, feed_url)

    soup = BeautifulSoup(resp.content, "xml")

    # RSS 2.0 は <item>、Atom は <entry>
    items = soup.find_all("item") or soup.find_all("entry")

    results: list[RssItem] = []
    for item in items[:max_items]:
        title_tag = item.find("title")
        title = _strip_html(title_tag.get_text() if title_tag else "")
        if not title:
            continue

        # URL
        link_tag = item.find("link")
        if link_tag:
            url = link_tag.get("href") or link_tag.get_text()
        else:
            url = ""
        url = url.strip() if url else ""

        # 日時
        pub_tag = item.find("pubDate") or item.find("published") or item.find("updated")
        published_at = _parse_datetime(pub_tag.get_text() if pub_tag else "")

        # 本文テキスト（description / content / summary）
        body_tag = (
            item.find("content:encoded")
            or item.find("content")
            or item.find("description")
            or item.find("summary")
        )
        body_text = _strip_html(body_tag.get_text() if body_tag else "")

        results.append(
            RssItem(
                title=title,
                url=url,
                published_at=published_at,
                source_name=source_name,
                source_type=source_type,
                body_text=body_text,
            )
        )

    return results


def fetch_page_text(url: str) -> str:
    """指定 URL の HTML ページからプレーンテキストを取得する。

    RSS の body_text が不十分な場合に使用する補助フェッチャー。
    """
    # javascript: スキームを禁止する
    if url.lower().strip().startswith("javascript:"):
        raise ValueError(f"Invalid URL scheme: {url}")

    with httpx.Client(
        timeout=settings.scraper_timeout,
        follow_redirects=True,
    ) as client:
        resp = _get_with_retry(client, url)

    return _strip_html(resp.text)
