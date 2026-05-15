"""HTML ニュース一覧スクレイパー。

RSS を公開していない政党サイトのニュース一覧ページから記事リンクを抽出し、
FetchResult のリストとして返す。
"""

from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from batch.scrapers.rss import _get_with_retry, _strip_html
from batch.settings import settings

_USER_AGENT = "Kuni-Musubi-Bot/1.0"


def _is_article_url(url: str, base_url: str) -> bool:
    """抽出した URL が記事リンクとして適切かどうかを判定する。

    ナビゲーション・フッター・外部リンクなどのノイズを除外する。
    """
    if not url or not url.startswith("http"):
        return False
    # 同一ドメインのリンクのみ対象にする
    base_host = urlparse(base_url).netloc
    link_host = urlparse(url).netloc
    if base_host and link_host and base_host != link_host:
        return False
    # ハッシュのみ・クエリのみのリンクを除外する
    parsed = urlparse(url)
    if not parsed.path or parsed.path in ("/", ""):
        return False
    return True


def fetch_html_index(
    site_url: str,
    base_url: str,
    link_selector: str,
    source_name: str,
    source_type: str = "party_official",
    max_items: int = 20,
) -> list[dict[str, str]]:
    """HTML ニュース一覧ページから記事リンクを抽出する。

    1. セーフティーガードを通じてニュース一覧ページを取得する
    2. CSS セレクタで記事リンクの <a> タグを抽出する
    3. 相対 URL を絶対 URL に変換する
    4. FetchResult 形式の辞書リストとして返す

    Args:
        site_url: スクレイプ対象のニュース一覧ページ URL
        base_url: 相対 URL を絶対 URL に変換するベースドメイン
        link_selector: 記事リンクを抽出する CSS セレクタ
        source_name: 出典政党名
        source_type: 出典種別
        max_items: 取得する記事リンクの最大件数

    Returns:
        FetchResult 互換の辞書リスト（title, source_url, source_name,
        source_type, published_at, body_text, feed_url を持つ）
    """
    # 1. ニュース一覧ページを取得する
    with httpx.Client(
        timeout=settings.scraper_timeout,
        follow_redirects=True,
    ) as client:
        resp = _get_with_retry(client, site_url)

    soup = BeautifulSoup(resp.text, "html.parser")

    # 2. CSS セレクタで <a> タグを抽出する
    if link_selector and link_selector.startswith("TODO"):
        # セレクタ未設定の場合はデフォルトで全 <a> タグを候補にする
        anchors = soup.find_all("a", href=True)
    else:
        try:
            anchors = soup.select(link_selector)
        except Exception:
            anchors = soup.find_all("a", href=True)

    results: list[dict[str, str]] = []
    seen_urls: set[str] = set()

    for anchor in anchors:
        href = anchor.get("href", "")
        if not href:
            continue

        # 3. 相対 URL を絶対 URL に変換する
        abs_url = urljoin(base_url or site_url, href)

        if not _is_article_url(abs_url, base_url or site_url):
            continue
        if abs_url in seen_urls:
            continue
        seen_urls.add(abs_url)

        # リンクテキストをタイトルとして使用する
        title = _strip_html(str(anchor)) or abs_url

        # 4. FetchResult 互換の辞書を生成する
        results.append(
            {
                "title": title,
                "source_url": abs_url,
                "source_name": source_name,
                "source_type": source_type,
                "published_at": datetime.now(tz=timezone.utc).isoformat(),
                "body_text": title,  # 本文は article_pipeline で補強される
                "feed_url": site_url,
            }
        )

        if len(results) >= max_items:
            break

    return results
