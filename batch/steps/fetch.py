"""記事フェッチステップ。

RSS フィードまたは HTML ニュース一覧から記事を取得し、
処理対象の FetchResult リストを返す。
parties.yml の type フィールドによって取得方式を動的に切り替える。
"""

import io
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlparse as _urlparse

import yaml

from batch.scrapers.rss import RssItem, fetch_rss

_CONFIG_PATH = Path(__file__).parent.parent / "config" / "parties.yml"

# parties.yml の type フィールドで使用する定数
_TYPE_RSS = "rss"
_TYPE_HTML_INDEX = "html_index"
_TYPE_DYNAMIC_DATE = "dynamic_date"
_TYPE_PDF = "pdf"
_TYPE_YOUTUBE = "youtube"


@dataclass
class FeedConfig:
    """フィード取得設定。RSS / HTML 一覧 / 動的日付 / PDF / YouTube に対応する。"""

    source_name: str
    source_type: str = "party_official"
    max_items: int = 20
    feed_type: str = _TYPE_RSS  # "rss" | "html_index" | "dynamic_date" | "pdf" | "youtube"
    # RSS 用フィールド
    url: str = ""
    # HTML 一覧 / dynamic_date 共通フィールド
    site_url: str = ""
    base_url: str = ""
    link_selector: str = ""
    # dynamic_date 用フィールド
    url_template: str = ""  # 例: "https://example.com/{YYYY}/{MM}/{DD}/"
    date_range_days: int = 2
    # タイトルフィルタ（全 type に適用）
    title_include: list[str] = field(default_factory=list)  # いずれかを含む場合のみ通過
    title_exclude: list[str] = field(default_factory=list)  # いずれかを含む場合はスキップ
    # YouTube 用フィールド
    playlist_id: str = ""


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
    media_type: str = "html"  # "html" | "pdf" | "youtube"


@dataclass
class ManualSource:
    """手動指定 URL ソース（CLI --url-list や admin 入力用）。"""

    url: str
    source_name: str = "manual"
    source_type: str = "party_official"


def detect_url_media_type(url: str) -> str:
    """URL の形式からメディア種別を判定する。

    Returns:
        "pdf" | "youtube" | "html"
    """
    lower = url.lower().split("?")[0]
    if lower.endswith(".pdf"):
        return "pdf"
    parsed = _urlparse(url)
    if "youtube.com" in parsed.netloc or "youtu.be" in parsed.netloc:
        return "youtube"
    return "html"


def _extract_youtube_video_id(url: str) -> str | None:
    """YouTube URL からビデオ ID を抽出する。"""
    parsed = _urlparse(url)
    if "youtube.com" in parsed.netloc:
        qs = parse_qs(parsed.query)
        ids = qs.get("v", [])
        return ids[0] if ids else None
    if "youtu.be" in parsed.netloc:
        return parsed.path.lstrip("/").split("/")[0] or None
    return None


def fetch_single_pdf_url(
    url: str,
    source_name: str = "manual",
    source_type: str = "party_official",
) -> FetchResult:
    """PDF URL から直接テキストを抽出して FetchResult を返す。

    1. PDF をメモリにダウンロードする
    2. pypdf でテキストを抽出する
    3. FetchResult を返す（テキストが空の場合は ValueError を送出する）
    """
    import httpx
    from pypdf import PdfReader

    from batch.scrapers.rss import _get_with_retry
    from batch.settings import settings

    # 1. PDF をメモリにダウンロードする
    with httpx.Client(timeout=settings.scraper_timeout, follow_redirects=True) as client:
        resp = _get_with_retry(client, url)

    # 2. pypdf でテキストを抽出する
    reader = PdfReader(io.BytesIO(resp.content))
    text_parts = [page.extract_text() for page in reader.pages if page.extract_text()]
    body_text = "\n".join(text_parts).strip()

    if not body_text:
        raise ValueError(
            f"テキスト抽出に失敗しました（画像のみの PDF の可能性があります）: {url}"
        )

    # 3. FetchResult を返す
    return FetchResult(
        title=url,
        source_url=url,
        source_name=source_name,
        source_type=source_type,
        published_at=datetime.now(tz=timezone.utc).isoformat(),
        body_text=body_text,
        feed_url=url,
        media_type="pdf",
    )


def _extract_pdf_text(pdf_url: str) -> str:
    """PDF URL からテキストを抽出する。"""
    import httpx
    from pypdf import PdfReader

    from batch.scrapers.rss import _get_with_retry
    from batch.settings import settings

    with httpx.Client(timeout=settings.scraper_timeout, follow_redirects=True) as client:
        pdf_resp = _get_with_retry(client, pdf_url)

    reader = PdfReader(io.BytesIO(pdf_resp.content))
    text_parts = [page.extract_text() for page in reader.pages if page.extract_text()]
    return _normalize_pdf_text("\n".join(text_parts).strip())


def _normalize_pdf_text(text: str) -> str:
    """PDF 抽出テキストを LLM に渡しやすい形へ正規化する。

    縦書き PDF は pypdf で 1 文字 1 行に抽出されることがあるため、
    短い行が連続するブロックだけを横書きの文章へ結合する。
    """
    if not text:
        return ""

    blocks = re.split(r"\n\s*\n", text)
    normalized_blocks: list[str] = []

    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        if _is_pdf_page_number_block(lines):
            continue

        short_lines = [line for line in lines if len(line) <= 3]
        total_chars = sum(len(line) for line in lines)
        is_vertical_like = (
            len(lines) >= 4
            and total_chars >= 4
            and len(short_lines) / len(lines) >= 0.75
        )

        if is_vertical_like:
            normalized_blocks.append("".join(lines))
        else:
            normalized_blocks.append("\n".join(lines))

    return _join_wrapped_pdf_blocks(normalized_blocks).strip()


def _is_pdf_page_number_block(lines: list[str]) -> bool:
    """PDF 抽出結果に混ざる孤立したページ番号ブロックを判定する。"""
    if len(lines) != 1:
        return False
    line = lines[0].strip()
    return bool(re.fullmatch(r"[0-9０-９一二三四五六七八九十百]{1,4}", line))


def _join_wrapped_pdf_blocks(blocks: list[str]) -> str:
    """ページ番号除去で分断された文を、句読点を手がかりに結合する。"""
    joined: list[str] = []
    sentence_endings = ("。", "．", ".", "」", "』", "？", "?", "！", "!")

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        if (
            joined
            and joined[-1]
            and len(joined[-1]) >= 40
            and len(block) >= 20
            and not joined[-1].endswith(sentence_endings)
            and not block.startswith(("質問内容PDF:", "答弁書PDF:"))
        ):
            joined[-1] = f"{joined[-1]}{block}"
        else:
            joined.append(block)

    return "\n\n".join(joined)


def fetch_single_youtube_url(
    url: str,
    source_name: str = "manual",
    source_type: str = "party_official",
) -> FetchResult:
    """YouTube URL から日本語字幕を取得して FetchResult を返す。

    1. URL からビデオ ID を抽出する
    2. youtube-transcript-api で日本語字幕を取得する
    3. FetchResult を返す（字幕が取得できない場合は ValueError を送出する）
    """
    from youtube_transcript_api import YouTubeTranscriptApi

    # 1. ビデオ ID を抽出する
    video_id = _extract_youtube_video_id(url)
    if not video_id:
        raise ValueError(f"YouTube URL からビデオ ID を抽出できません: {url}")

    # 2. 日本語字幕を取得する（v1.x インスタンス API）
    try:
        fetched = YouTubeTranscriptApi().fetch(video_id, languages=["ja"])
    except Exception as exc:
        raise ValueError(
            f"テキスト抽出に失敗しました（字幕なしまたは無効な動画）: {url} — {exc}"
        ) from exc

    body_text = " ".join(segment.text for segment in fetched).strip()
    if not body_text:
        raise ValueError(f"テキスト抽出に失敗しました（字幕テキストが空）: {url}")

    # 3. FetchResult を返す
    return FetchResult(
        title=url,
        source_url=url,
        source_name=source_name,
        source_type=source_type,
        published_at=datetime.now(tz=timezone.utc).isoformat(),
        body_text=body_text,
        feed_url=url,
        media_type="youtube",
    )


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
            print(f"[fetch] スキップ（設定未完了）: {feed.get('source_name', '?')}")
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
                url_template=feed.get("url_template", ""),
                date_range_days=feed.get("date_range_days", 2),
                title_include=feed.get("title_include", []),
                title_exclude=feed.get("title_exclude", []),
                playlist_id=feed.get("playlist_id", ""),
            )
        )
    return configs


def _apply_title_filters(
    results: list[FetchResult],
    title_include: list[str],
    title_exclude: list[str],
) -> list[FetchResult]:
    """タイトルフィルタを適用する。

    title_include が指定されている場合は、いずれかのキーワードを含む記事のみ通過させる。
    title_exclude が指定されている場合は、いずれかのキーワードを含む記事をスキップする。
    """
    if title_include:
        results = [r for r in results if any(kw in r.title for kw in title_include)]
    if title_exclude:
        results = [r for r in results if not any(kw in r.title for kw in title_exclude)]
    return results


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


def _fetch_dynamic_date_items(feed: FeedConfig) -> list[FetchResult]:
    """動的に生成した日付 URL から記事を取得する（公明党など）。

    url_template 内の {YYYY} {MM} {DD} を実行日基準の日付で置換し、
    date_range_days 日分の URL を html_index として取得する。
    """
    results: list[FetchResult] = []
    today = date.today()
    for i in range(feed.date_range_days):
        d = today - timedelta(days=i)
        url = feed.url_template.format(
            YYYY=d.strftime("%Y"),
            MM=d.strftime("%m"),
            DD=d.strftime("%d"),
        )
        try:
            sub_feed = FeedConfig(
                source_name=feed.source_name,
                source_type=feed.source_type,
                max_items=feed.max_items,
                feed_type=_TYPE_HTML_INDEX,
                site_url=url,
                base_url=feed.base_url,
                link_selector=feed.link_selector,
            )
            items = _fetch_html_index_items(sub_feed)
            results.extend(items)
            print(f"[fetch] 動的日付URL取得: {url} → {len(items)} 件")
        except Exception as exc:
            print(f"[fetch] 動的日付URL取得失敗: {url} — {exc}")
    return results


def _fetch_pdf_items(feed: FeedConfig) -> list[FetchResult]:
    """HTML ページ内の PDF リンクを取得してテキスト抽出する（日本保守党など）。

    1. site_url をフェッチして PDF リンクを抽出する
    2. 各 PDF をメモリにダウンロードする
    3. pypdf でテキストを抽出して body_text に代入する
    """
    import httpx

    from bs4 import BeautifulSoup

    from batch.scrapers.rss import _get_with_retry
    from batch.settings import settings

    # 1. HTML ページから PDF リンクを抽出する
    with httpx.Client(timeout=settings.scraper_timeout, follow_redirects=True) as client:
        resp = _get_with_retry(client, feed.site_url)

    soup = BeautifulSoup(resp.text, "html.parser")

    if feed.source_name == "日本保守党":
        return _fetch_hoshuto_pdf_pairs(feed, soup)

    pdf_links: list[tuple[str, str]] = []
    for anchor in soup.find_all("a", href=True):
        href = str(anchor.get("href", ""))
        if href.lower().endswith(".pdf"):
            abs_url = urljoin(feed.base_url or feed.site_url, href)
            title = anchor.get_text(strip=True) or abs_url
            pdf_links.append((abs_url, title))

    if not pdf_links:
        print(f"[fetch] PDF リンクが見つかりません: {feed.site_url}")
        return []

    results: list[FetchResult] = []
    for pdf_url, title in pdf_links[: feed.max_items]:
        try:
            # 2. PDF をメモリにダウンロードし、pypdf でテキストを抽出する
            body_text = _extract_pdf_text(pdf_url)

            if not body_text:
                print(f"[fetch] PDF テキスト抽出結果が空: {pdf_url}")
                continue

            results.append(
                FetchResult(
                    title=title,
                    source_url=pdf_url,
                    source_name=feed.source_name,
                    source_type=feed.source_type,
                    published_at=datetime.now(tz=timezone.utc).isoformat(),
                    body_text=body_text,
                    feed_url=feed.site_url,
                    media_type="pdf",
                )
            )
        except Exception as exc:
            print(f"[fetch] PDF 取得・抽出失敗: {pdf_url} — {exc}")

    return results


def _extract_hoshuto_pdf_key(pdf_url: str) -> str | None:
    """日本保守党の質問・答弁 PDF URL から同一質問を表す番号を抽出する。"""
    match = re.search(r"/[ab](\d+)\.pdf(?:/|\?|$)", pdf_url)
    if match:
        return match.group(1)
    return None


def _find_hoshuto_card_title(anchor: object) -> str:
    """日本保守党の PDF リンク付近から質問タイトルを推定する。"""
    find_parent = getattr(anchor, "find_parent", None)
    if not callable(find_parent):
        return ""

    container = find_parent(
        "div",
        class_=lambda value: bool(value) and "has-background" in value,
    )
    if container:
        heading = container.find(["h4", "h3"])
        if heading:
            return heading.get_text(" ", strip=True)
    return ""


def _fetch_hoshuto_pdf_pairs(feed: FeedConfig, soup: object) -> list[FetchResult]:
    """日本保守党の国会活動ページから質問内容・答弁書 PDF をペア化して取得する。"""
    pairs: dict[str, dict[str, str]] = {}

    for anchor in soup.find_all("a", href=True):  # type: ignore[attr-defined]
        href = str(anchor.get("href", ""))
        if not href.lower().endswith(".pdf"):
            continue

        pdf_url = urljoin(feed.base_url or feed.site_url, href)
        key = _extract_hoshuto_pdf_key(pdf_url)
        if not key:
            continue

        label = anchor.get_text(" ", strip=True)
        pair = pairs.setdefault(key, {"title": "", "question_url": "", "answer_url": ""})
        if not pair["title"]:
            pair["title"] = _find_hoshuto_card_title(anchor)

        lower_pdf_url = pdf_url.lower()
        if "質問内容" in label or "pdf_s" in lower_pdf_url or "/pdfs/" in lower_pdf_url:
            pair["question_url"] = pdf_url
        elif "答弁書" in label or "pdf_t" in lower_pdf_url or "/pdft/" in lower_pdf_url:
            pair["answer_url"] = pdf_url

    results: list[FetchResult] = []
    complete_pairs = [
        pair
        for pair in pairs.values()
        if pair.get("question_url") and pair.get("answer_url")
    ]

    for pair in complete_pairs[: feed.max_items]:
        question_url = pair["question_url"]
        answer_url = pair["answer_url"]
        title = pair["title"] or "質問内容・答弁書"

        try:
            question_text = _extract_pdf_text(question_url)
            answer_text = _extract_pdf_text(answer_url)
        except Exception as exc:
            print(f"[fetch] 日本保守党 PDF ペア取得・抽出失敗: {question_url} — {exc}")
            continue

        if not question_text or not answer_text:
            print(f"[fetch] 日本保守党 PDF ペアのテキスト抽出結果が空: {question_url}")
            continue

        body_text = "\n\n".join(
            [
                f"質問内容PDF: {question_url}",
                question_text,
                f"答弁書PDF: {answer_url}",
                answer_text,
            ]
        )

        results.append(
            FetchResult(
                title=title,
                source_url=question_url,
                source_name=feed.source_name,
                source_type=feed.source_type,
                published_at=datetime.now(tz=timezone.utc).isoformat(),
                body_text=body_text,
                feed_url=feed.site_url,
                media_type="pdf",
            )
        )

    if not results:
        print(f"[fetch] 日本保守党の質問内容・答弁書 PDF ペアが見つかりません: {feed.site_url}")

    return results


def _fetch_youtube_items(feed: FeedConfig) -> list[FetchResult]:
    """YouTube プレイリストの RSS から最新動画の日本語字幕を取得する（日本共産党など）。

    1. feedparser でプレイリスト RSS を読み込む
    2. 最新エントリからビデオ ID を取得する
    3. youtube-transcript-api で日本語字幕を取得してプレーンテキストに結合する
    """
    import time as time_module

    import feedparser
    from youtube_transcript_api import YouTubeTranscriptApi

    rss_url = (
        f"https://www.youtube.com/feeds/videos.xml?playlist_id={feed.playlist_id}"
    )
    parsed = feedparser.parse(rss_url)

    if not parsed.entries:
        print(f"[fetch] YouTube RSS エントリが空: {rss_url}")
        return []

    results: list[FetchResult] = []
    for entry in parsed.entries[: feed.max_items]:
        # feedparser の yt 拡張属性または link から video_id を取得する
        video_id: str = entry.get("yt_videoid", "")
        if not video_id:
            link = entry.get("link", "")
            if "v=" in link:
                video_id = link.split("v=")[-1].split("&")[0]
        if not video_id:
            continue

        title: str = entry.get("title", video_id)
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # 公開日を変換する
        published_at: str
        if entry.get("published_parsed"):
            pub_dt = datetime.fromtimestamp(
                time_module.mktime(entry.published_parsed), tz=timezone.utc
            )
            published_at = pub_dt.isoformat()
        else:
            published_at = datetime.now(tz=timezone.utc).isoformat()

        try:
            # 3. 日本語字幕を取得してプレーンテキストに結合する（v1.x インスタンス API）
            fetched = YouTubeTranscriptApi().fetch(video_id, languages=["ja"])
            body_text = " ".join(segment.text for segment in fetched).strip()

            if not body_text:
                print(f"[fetch] YouTube 字幕が空: {video_id}")
                continue

            results.append(
                FetchResult(
                    title=title,
                    source_url=video_url,
                    source_name=feed.source_name,
                    source_type=feed.source_type,
                    published_at=published_at,
                    body_text=body_text,
                    feed_url=rss_url,
                    media_type="youtube",
                )
            )
        except Exception as exc:
            print(f"[fetch] YouTube 字幕取得失敗: {video_id} — {exc}")

    return results


def fetch_articles_from_feeds(feeds: list[FeedConfig]) -> list[FetchResult]:
    """複数のフィード設定から記事を取得してフェッチ結果リストを返す。

    1. 各フィードの feed_type を確認して適切なハンドラを呼ぶ
    2. タイトルフィルタ（title_include / title_exclude）を適用する
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
            elif feed.feed_type == _TYPE_DYNAMIC_DATE:
                items = _fetch_dynamic_date_items(feed)
            elif feed.feed_type == _TYPE_PDF:
                items = _fetch_pdf_items(feed)
            elif feed.feed_type == _TYPE_YOUTUBE:
                items = _fetch_youtube_items(feed)
            else:
                print(f"[fetch] 未知の feed_type をスキップ: {feed_label}")
                continue
        except Exception as exc:
            print(f"[fetch] フィード取得失敗: {feed_label} — {exc}")
            continue

        # 2. タイトルフィルタを適用する
        before = len(items)
        items = _apply_title_filters(items, feed.title_include, feed.title_exclude)
        if before != len(items):
            print(f"[fetch] タイトルフィルタ: {before} → {len(items)} 件 ({feed.source_name})")

        results.extend(items)
        print(f"[fetch] 取得完了: {feed_label} {len(items)} 件")

    return results
