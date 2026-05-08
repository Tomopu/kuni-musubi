"""政党公式サイトから RSS フィードを探索し、config/parties.yml を更新する。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree

import httpx
import yaml
from bs4 import BeautifulSoup

TIMEOUT_SECONDS = 3.0
CONFIG_PATH = Path(__file__).parent / "config" / "parties.yml"
USER_AGENT = (
    "Kuni-Musubi feed verifier/1.0 "
    "(https://github.com/kuni-musubi; RSS auto-discovery)"
)

PARTY_TOP_URLS: dict[str, str] = {
    "自由民主党": "https://www.jimin.jp/",
    "立憲民主党": "https://cdp-japan.jp/",
    "国民民主党": "https://new-kokumin.jp/",
    "公明党": "https://www.komei.or.jp/",
    "日本維新の会": "https://o-ishin.jp/",
    "参政党": "https://sanseito.jp/",
    "日本共産党": "https://www.jcp.or.jp/",
    "れいわ新選組": "https://reiwa-shinsengumi.com/",
    "日本保守党": "https://hoshuto.jp/",
    "社会民主党": "https://sdp.or.jp/",
    "チームみらい": "https://team-mir.ai/",
    "中道改革連合": "https://craj.jp",
    "減税日本・ゆうこく連合": "http://genzeiyukoku.jp",
}

COMMON_FEED_PATHS = (
    "/rss",
    "/rss/",
    "/feed",
    "/feed/",
    "/feeds",
    "/feeds/",
    "/news/rss.xml",
    "/news/feed",
    "/news/feed/",
    "/news/index.rdf",
    "/news/rss",
    "/news/rss/",
    "/topics/rss.xml",
    "/information/rss.xml",
    "/wp/feed/",
    "/?feed=rss2",
)

FEED_CONTENT_TYPES = (
    "application/rss+xml",
    "application/atom+xml",
    "application/rdf+xml",
    "application/xml",
    "text/xml",
)


@dataclass(frozen=True)
class FeedResult:
    name: str
    type: str
    url: str
    base_url: str | None = None
    link_selector: str | None = None


def normalize_base_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return ""
    return f"{parsed.scheme}://{parsed.netloc}"


def safe_get(client: httpx.Client, url: str) -> httpx.Response | None:
    try:
        response = client.get(url)
        return response
    except httpx.HTTPError:
        return None


def is_xml_parseable(content: bytes) -> bool:
    try:
        ElementTree.fromstring(content)
    except ElementTree.ParseError:
        return False
    return True


def is_valid_feed(client: httpx.Client, url: str) -> bool:
    response = safe_get(client, url)
    if response is None or response.status_code != 200:
        return False
    if not response.content:
        return False
    return is_xml_parseable(response.content)


def is_feed_link_type(value: str) -> bool:
    lowered = value.lower().split(";")[0].strip()
    return lowered in FEED_CONTENT_TYPES or "rss" in lowered or "atom" in lowered


def discover_from_html(page_url: str, html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    candidates: list[str] = []
    for tag in soup.find_all("link"):
        href = tag.get("href")
        if not href:
            continue
        rel_values = tag.get("rel") or []
        rel = (
            " ".join(rel_values).lower()
            if isinstance(rel_values, list)
            else str(rel_values).lower()
        )
        type_value = str(tag.get("type") or "")
        if "alternate" not in rel:
            continue
        if not is_feed_link_type(type_value):
            continue
        candidates.append(urljoin(page_url, href))
    return candidates


def common_feed_candidates(top_url: str) -> list[str]:
    base_url = normalize_base_url(top_url)
    if not base_url:
        return []
    return [urljoin(base_url, path) for path in COMMON_FEED_PATHS]


def unique_urls(urls: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for url in urls:
        if url in seen:
            continue
        seen.add(url)
        result.append(url)
    return result


def find_feed_url(client: httpx.Client, top_url: str) -> str | None:
    if not top_url:
        return None

    candidates: list[str] = []
    response = safe_get(client, top_url)
    if response is not None and response.status_code == 200:
        content_type = response.headers.get("content-type", "")
        if "html" in content_type.lower() or response.text:
            candidates.extend(discover_from_html(str(response.url), response.text))

    candidates.extend(common_feed_candidates(top_url))
    for candidate in unique_urls(candidates):
        if is_valid_feed(client, candidate):
            return candidate
    return None


def fallback_url(top_url: str) -> str:
    return top_url or ""


def build_result(client: httpx.Client, name: str, top_url: str) -> FeedResult:
    feed_url = find_feed_url(client, top_url)
    if feed_url:
        return FeedResult(name=name, type="rss", url=feed_url)

    return FeedResult(
        name=name,
        type="html_index",
        url=fallback_url(top_url),
        base_url=normalize_base_url(top_url),
        link_selector="TODO: 記事リンクのCSSセレクタ",
    )


def result_to_yaml_item(result: FeedResult) -> dict[str, Any]:
    item: dict[str, Any] = {
        "name": result.name,
        "type": result.type,
        "url": result.url,
    }
    if result.type == "html_index":
        item["base_url"] = result.base_url or ""
        item["link_selector"] = result.link_selector
    return item


def write_config(results: list[FeedResult], path: Path = CONFIG_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"parties": [result_to_yaml_item(result) for result in results]}
    with path.open("w", encoding="utf-8") as f:
        f.write("# 政党ごとの公式サイト取得設定。verify_feeds.py により生成。\n")
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)


def main() -> None:
    headers = {"User-Agent": USER_AGENT}
    limits = httpx.Limits(max_connections=4, max_keepalive_connections=2)
    results: list[FeedResult] = []
    with httpx.Client(
        headers=headers,
        timeout=TIMEOUT_SECONDS,
        follow_redirects=True,
        limits=limits,
    ) as client:
        for name, top_url in PARTY_TOP_URLS.items():
            result = build_result(client, name, top_url)
            results.append(result)
            print(f"{name}: {result.type} {result.url}")

    write_config(results)
    print(f"updated: {CONFIG_PATH}")


if __name__ == "__main__":
    main()
