"""記事フェッチステップ。

RSS フィードを取得し、処理対象の FetchResult リストを返す。
"""

from dataclasses import dataclass

from batch.scrapers.rss import RssItem, fetch_rss


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
