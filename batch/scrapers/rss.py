"""RSS フィード取得スクレイパー。"""

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html import unescape
from typing import Any

import httpx
from bs4 import BeautifulSoup

from batch.settings import settings


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


def fetch_rss(
    feed_url: str,
    source_name: str,
    source_type: str = "news_media",
    max_items: int | None = None,
) -> list[RssItem]:
    """RSS フィードを取得してパースした結果を返す。

    1. HTTP GET でフィードを取得する
    2. BeautifulSoup で item/entry 要素をパースする
    3. RssItem のリストとして返す
    """
    if max_items is None:
        max_items = settings.rss_max_items

    with httpx.Client(
        timeout=settings.scraper_timeout,
        follow_redirects=True,
    ) as client:
        resp = client.get(feed_url, headers={"User-Agent": "Kuni-Musubi-Bot/1.0"})
        resp.raise_for_status()

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
        resp = client.get(url, headers={"User-Agent": "Kuni-Musubi-Bot/1.0"})
        resp.raise_for_status()

    return _strip_html(resp.text)
