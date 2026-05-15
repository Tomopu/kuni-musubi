"""HTML 本文抽出パーサー。

URL または HTML 文字列から記事の本文テキストのみを抽出する。
余分なナビゲーション・広告・スクリプトを除去し、LLM に渡す品質の高いテキストを返す。
"""

import re
from html import unescape

import httpx
from bs4 import BeautifulSoup

from batch.scrapers.rss import _get_with_retry
from batch.settings import settings

# 本文に含まれないノイズタグ
_NOISE_TAGS = frozenset(
    {"script", "style", "nav", "header", "footer", "aside", "form", "iframe", "noscript"}
)

# 本文コンテナの id/class に含まれる可能性が高いキーワード
_CONTENT_ID_PATTERN = re.compile(r"(content|article|main|body|post|entry)", re.I)
_CONTENT_CLASS_PATTERN = re.compile(
    r"(content|article|main|body|post|entry|text|news)", re.I
)


def extract_article_text(html: str) -> str:
    """HTML 文字列から記事本文のプレーンテキストを抽出する。

    1. ノイズタグ（script, style, nav など）を除去する
    2. <article> → <main> → id/class にキーワードを含む <div> の順でコンテナを探す
    3. コンテナが見つからない場合は全 <p> タグのテキストを結合する
    4. 連続する空白・改行を圧縮してプレーンテキストを返す
    """
    soup = BeautifulSoup(html, "html.parser")

    # 1. ノイズタグを除去する
    for tag_name in _NOISE_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    # 2. コンテナを順番に探す
    container = (
        soup.find("article")
        or soup.find("main")
        or soup.find("div", id=_CONTENT_ID_PATTERN)
        or soup.find("div", class_=_CONTENT_CLASS_PATTERN)
    )

    if container:
        text = container.get_text(separator="\n")
    else:
        # 3. コンテナが見つからない場合は全 <p> タグを結合する
        paragraphs = soup.find_all("p")
        text = "\n".join(p.get_text() for p in paragraphs)

    # 4. 連続する空白・改行を圧縮する
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return unescape(text).strip()


def fetch_article_text(url: str) -> str:
    """指定 URL から記事本文のプレーンテキストを取得する。

    セーフティーガード（_get_with_retry）を経由してアクセスする。

    1. URL スキームを検証する
    2. セーフティーガードを通じて HTTP GET でページを取得する
    3. extract_article_text で本文テキストを抽出して返す
    """
    if url.lower().strip().startswith("javascript:"):
        raise ValueError(f"Invalid URL scheme: {url}")

    with httpx.Client(
        timeout=settings.scraper_timeout,
        follow_redirects=True,
    ) as client:
        resp = _get_with_retry(client, url)

    return extract_article_text(resp.text)
