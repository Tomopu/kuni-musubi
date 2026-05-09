"""記事フェッチステップ。

RSS フィードまたは HTML ニュース一覧から記事を取得し、
処理対象の FetchResult リストを返す。
parties.yml の type フィールドによって取得方式を動的に切り替える。
"""

from dataclasses import dataclass
from pathlib import Path

import yaml

from batch.scrapers.rss import RssItem, fetch_rss

_CONFIG_PATH = Path(__file__).parent.parent / "config" / "parties.yml"

# parties.yml の type フィールドで使用する定数
_TYPE_RSS = "rss"
_TYPE_HTML_INDEX = "html_index"


@dataclass
class FeedConfig:
    """フィード取得設定。RSS と HTML 一覧の両方に対応する。"""

    source_name: str
    source_type: str = "party_official"
    max_items: int = 20
    feed_type: str = _TYPE_RSS  # "rss" | "html_index"
    # RSS 用フィールド
    url: str = ""
    # HTML 一覧用フィールド
    site_url: str = ""
    base_url: str = ""
    link_selector: str = ""


@dataclass
class FetchResult:
    """フェッチ済み記事の中間データ。"""

    title: str
    source_url: str
    source_name: str
    source_type: str
    published_at: str  # ISO 8601 文字列
    body_text: str
    feed_url: str


@dataclass
class ManualSource:
    """手動指定 URL ソース（CLI --url-list や admin 入力用）。"""

    url: str
    source_name: str = "manual"
    source_type: str = "party_official"


def load_feeds_from_config(config_path: Path = _CONFIG_PATH) -> list[FeedConfig]:
    """parties.yml から FeedConfig のリストを読み込む。

    1. YAML ファイルを読み込む
    2. feeds リストを FeedConfig に変換する（type フィールドで切り替え）
    3. site_url または url が未設定のエントリはスキップする
    4. FeedConfig のリストを返す
    """
    with config_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    configs: list[FeedConfig] = []
    for feed in data.get("feeds", []):
        feed_type = feed.get("type", _TYPE_RSS)
        site_url = feed.get("site_url", "")
        url = feed.get("url", "")
        base_url = feed.get("base_url", "")

        # TODO が残っているエントリはスキップする
        if site_url.startswith("TODO") or base_url.startswith("TODO"):
            print(
                f"[fetch] スキップ（設定未完了）: {feed.get('source_name', '?')}"
            )
            continue

        configs.append(
            FeedConfig(
                source_name=feed["source_name"],
                source_type=feed.get("source_type", "party_official"),
                max_items=feed.get("max_items", 20),
                feed_type=feed_type,
                url=url,
                site_url=site_url,
                base_url=base_url,
                link_selector=feed.get("link_selector", ""),
            )
        )
    return configs


def _fetch_rss_items(feed: FeedConfig) -> list[FetchResult]:
    """RSS フィードから記事を取得して FetchResult リストに変換する。"""
    items: list[RssItem] = fetch_rss(
        feed_url=feed.url,
        source_name=feed.source_name,
        source_type=feed.source_type,
        max_items=feed.max_items,
    )
    results: list[FetchResult] = []
    for item in items:
        if not item.url:
            continue
        results.append(
            FetchResult(
                title=item.title,
                source_url=item.url,
                source_name=item.source_name,
                source_type=item.source_type,
                published_at=item.published_at.isoformat(),
                body_text=item.body_text or item.title,
                feed_url=feed.url,
            )
        )
    return results


def _fetch_html_index_items(feed: FeedConfig) -> list[FetchResult]:
    """HTML ニュース一覧ページから記事リンクを取得して FetchResult リストに変換する。"""
    from batch.scrapers.html_index_scraper import fetch_html_index

    raw_items = fetch_html_index(
        site_url=feed.site_url,
        base_url=feed.base_url,
        link_selector=feed.link_selector,
        source_name=feed.source_name,
        source_type=feed.source_type,
        max_items=feed.max_items,
    )
    return [
        FetchResult(
            title=item["title"],
            source_url=item["source_url"],
            source_name=item["source_name"],
            source_type=item["source_type"],
            published_at=item["published_at"],
            body_text=item["body_text"],
            feed_url=item["feed_url"],
        )
        for item in raw_items
    ]


def fetch_articles_from_feeds(feeds: list[FeedConfig]) -> list[FetchResult]:
    """複数のフィード設定から記事を取得してフェッチ結果リストを返す。

    1. 各フィードの feed_type を確認する
    2. rss タイプは RSS スクレイパーで、html_index タイプは HTML スクレイパーで取得する
    3. 全フィードの結果を結合して返す
    """
    results: list[FetchResult] = []

    for feed in feeds:
        feed_label = f"{feed.source_name}({feed.feed_type})"
        try:
            if feed.feed_type == _TYPE_RSS:
                items = _fetch_rss_items(feed)
            elif feed.feed_type == _TYPE_HTML_INDEX:
                items = _fetch_html_index_items(feed)
            else:
                print(f"[fetch] 未知の feed_type をスキップ: {feed_label}")
                continue
        except Exception as exc:
            print(f"[fetch] フィード取得失敗: {feed_label} — {exc}")
            continue

        results.extend(items)
        print(f"[fetch] 取得完了: {feed_label} {len(items)} 件")

    return results
