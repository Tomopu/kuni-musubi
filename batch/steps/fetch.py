"""記事フェッチステップ。

RSS フィードを取得し、処理対象の FetchResult リストを返す。
"""

from dataclasses import dataclass
from pathlib import Path

import yaml

from batch.scrapers.rss import RssItem, fetch_rss

_CONFIG_PATH = Path(__file__).parent.parent / "config" / "parties.yml"


@dataclass
class FeedConfig:
    """RSS フィードの設定。"""

    url: str
    source_name: str
    source_type: str = "news_media"
    max_items: int = 20


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


def load_feeds_from_config(config_path: Path = _CONFIG_PATH) -> list[FeedConfig]:
    """parties.yml から FeedConfig のリストを読み込む。

    1. YAML ファイルを読み込む
    2. feeds リストを FeedConfig に変換する
    3. FeedConfig のリストを返す
    """
    with config_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return [
        FeedConfig(
            url=feed["url"],
            source_name=feed["source_name"],
            source_type=feed.get("source_type", "news_media"),
            max_items=feed.get("max_items", 20),
        )
        for feed in data.get("feeds", [])
    ]


def fetch_articles_from_feeds(feeds: list[FeedConfig]) -> list[FetchResult]:
    """複数の RSS フィードを取得してフェッチ結果リストを返す。

    1. 各フィードを順番に取得する
    2. RssItem を FetchResult に変換する
    3. 全フィードの結果を結合して返す
    """
    results: list[FetchResult] = []

    for feed in feeds:
        try:
            items: list[RssItem] = fetch_rss(
                feed_url=feed.url,
                source_name=feed.source_name,
                source_type=feed.source_type,
                max_items=feed.max_items,
            )
        except Exception as exc:
            # フィード取得失敗時はスキップしてログ出力
            print(f"[fetch] フィード取得失敗: {feed.url} — {exc}")
            continue

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
