"""記事収集パイプライン。

RSS フィードを取得 → LLM 処理 → DB 保存の一連のフローを実行する。
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable
from urllib.parse import urljoin, urlparse, urlunparse

import httpx
from bs4 import BeautifulSoup

from batch.db.session import SessionLocal
from batch.scrapers.html_parser import fetch_article_text
from batch.scrapers.rss import _get_with_retry
from batch.settings import settings
from batch.steps.fetch import (
    FeedConfig,
    FetchResult,
    ManualSource,
    detect_url_media_type,
    fetch_articles_from_feeds,
    fetch_single_pdf_url,
    fetch_single_youtube_url,
    load_feeds_from_config,
)
from batch.steps.llm_process import process_article_with_llm
from batch.steps.save import save_article

# この文字数未満の本文は URL からフル本文を取得して補強する
_MIN_BODY_LENGTH = 300
_MAX_AUTO_SUPPLEMENTAL_PDFS = 3


@dataclass
class PipelineResult:
    """パイプライン実行結果のサマリ。"""

    total_fetched: int = 0
    total_skipped: int = 0
    total_processed: int = 0
    total_saved: int = 0
    saved_article_ids: list[uuid.UUID] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PipelineEvent:
    """パイプライン進捗イベント。"""

    level: str  # info | warning | error
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)


def _emit(
    callback: "Callable[[PipelineEvent], None] | None",
    level: str,
    message: str,
    **kwargs: Any,
) -> None:
    """print を実行し、コールバックが設定されていれば PipelineEvent を送信する。"""
    print(message)
    if callback:
        callback(PipelineEvent(level=level, message=message, metadata=dict(kwargs)))


def _normalize_url(url: str) -> str:
    """URL を正規化する（空白除去、fragment 除去、query パラメータ保持）。"""
    url = url.strip()
    parsed = urlparse(url)
    return urlunparse(
        (parsed.scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, "")
    )


def _fetch_single_url(url: str) -> "FetchResult":
    """URL の種別を自動判定してフェッチ結果を返す。

    1. URL 形式からメディア種別を判定する
    2. PDF → pypdf でテキスト抽出
    3. YouTube → youtube-transcript-api で字幕取得
    4. それ以外 → HTML スクレイピング
    """
    # 1. メディア種別を判定する
    media_type = detect_url_media_type(url)

    # 2. PDF 処理
    if media_type == "pdf":
        return fetch_single_pdf_url(url)

    # 3. YouTube 処理
    if media_type == "youtube":
        return fetch_single_youtube_url(url)

    # 4. HTML スクレイピング
    body_text = fetch_article_text(url)
    return FetchResult(
        title=url,
        source_url=_normalize_url(url),
        source_name="manual",
        source_type="manual",
        published_at=datetime.now(timezone.utc).isoformat(),
        body_text=body_text,
        feed_url=url,
        media_type="html",
    )


def _extract_pdf_links_from_html(url: str) -> list[str]:
    """HTML ページ内の PDF リンクを絶対URLで返す。"""
    with httpx.Client(
        timeout=settings.scraper_timeout,
        follow_redirects=True,
    ) as client:
        resp = _get_with_retry(client, url)

    soup = BeautifulSoup(resp.text, "html.parser")
    links: list[str] = []
    seen: set[str] = set()
    for anchor in soup.find_all("a", href=True):
        href = str(anchor.get("href", "")).strip()
        if not href.lower().split("?", 1)[0].endswith(".pdf"):
            continue
        pdf_url = _normalize_url(urljoin(url, href))
        if pdf_url in seen:
            continue
        seen.add(pdf_url)
        links.append(pdf_url)
    return links


def _append_supplemental_urls(
    fetch_result: FetchResult,
    urls: list[str],
    progress_callback: "Callable[[PipelineEvent], None] | None",
) -> None:
    """補足資料URLを取得して FetchResult の本文末尾に追記する。"""
    sections: list[str] = []
    primary_url = _normalize_url(fetch_result.source_url)
    seen: set[str] = {primary_url}
    for url in urls:
        normalized_url = _normalize_url(url)
        if not normalized_url or normalized_url in seen:
            continue
        seen.add(normalized_url)
        try:
            _emit(
                progress_callback,
                "info",
                f"[pipeline] 補足資料取得開始: {normalized_url}",
            )
            supplemental = _fetch_single_url(normalized_url)
        except Exception as exc:
            _emit(
                progress_callback,
                "warning",
                f"[pipeline] 補足資料取得失敗（継続）: {normalized_url} — {exc}",
            )
            continue
        if not supplemental.body_text:
            continue
        sections.append(
            "\n\n".join(
                [
                    "---- 補足資料 ----",
                    f"URL: {supplemental.source_url}",
                    f"種別: {supplemental.media_type}",
                    supplemental.body_text,
                ]
            )
        )
        _emit(
            progress_callback,
            "info",
            "[pipeline] 補足資料取得成功: "
            f"{len(supplemental.body_text)} 文字 {normalized_url}",
        )

    if sections:
        fetch_result.body_text = "\n\n".join(
            [fetch_result.body_text, *sections]
        ).strip()


def _append_auto_supplemental_pdfs(
    fetch_result: FetchResult,
    progress_callback: "Callable[[PipelineEvent], None] | None",
) -> None:
    """自民党HTML記事に添付されたPDFを補足資料として本文に追記する。"""
    if fetch_result.media_type != "html" or fetch_result.source_name != "自由民主党":
        return
    try:
        pdf_urls = _extract_pdf_links_from_html(fetch_result.source_url)
    except Exception as exc:
        _emit(
            progress_callback,
            "warning",
            f"[pipeline] 添付PDF検出失敗（継続）: {fetch_result.source_url} — {exc}",
        )
        return
    if not pdf_urls:
        return
    _append_supplemental_urls(
        fetch_result,
        pdf_urls[:_MAX_AUTO_SUPPLEMENTAL_PDFS],
        progress_callback,
    )


def run_article_pipeline(
    feeds: list[FeedConfig] | None = None,
    dry_run: bool = False,
    fetch_only: bool = False,
    single_url: str | None = None,
    single_source_name: str = "manual",
    single_source_type: str = "party_official",
    supplemental_urls: list[str] | None = None,
    url_sources: list[ManualSource] | None = None,
    progress_callback: "Callable[[PipelineEvent], None] | None" = None,
) -> PipelineResult:
    """記事収集パイプラインを実行する。

    1. RSS フィードから記事を取得する
    2. fetch_only=True の場合はフェッチ結果を表示して終了する
    3. 最大件数の上限を適用する
    4. 本文が短い記事は URL からフル本文を補強する
    5. 各記事を LLM で処理する
    6. 処理結果を DB に保存する（dry_run=True のときは保存しない）

    Args:
        feeds: RSS フィード設定リスト。None のときは parties.yml を読み込む。
        dry_run: True のときは DB 保存をスキップする。
        fetch_only: True のときは LLM 処理・DB 保存をスキップする。
        single_url: 指定した URL 1件のみを処理する。
        single_source_name: single_url の出典名。
        single_source_type: single_url の出典種別。
        supplemental_urls: single_url に追記する補足資料URLリスト。
        url_sources: 手動指定 URL ソースのリスト。CLI --url-list や admin 入力用。
        progress_callback: 進捗イベントを受け取るコールバック。

    Returns:
        PipelineResult: 実行結果サマリ。
    """
    result = PipelineResult()
    if feeds is None:
        feeds = load_feeds_from_config()

    # 1. フィードまたは URL リストまたは単一 URL から記事を取得する
    if single_url:
        normalized = _normalize_url(single_url)
        media_type = detect_url_media_type(normalized)
        _emit(progress_callback, "info", f"[pipeline] 単一 URL モード: {normalized}")
        if media_type == "pdf":
            _emit(progress_callback, "info", "[pdf] ページ解析中...")
        elif media_type == "youtube":
            _emit(progress_callback, "info", "[youtube] 字幕取得中...")
        try:
            fetch_results: list[FetchResult] = [_fetch_single_url(single_url)]
        except ValueError as exc:
            _emit(
                progress_callback,
                "error",
                f"[pipeline] テキスト抽出に失敗しました: {exc}",
            )
            result.errors.append(str(exc))
            return result
        except Exception as exc:
            _emit(progress_callback, "error", f"[pipeline] URL 取得エラー: {exc}")
            result.errors.append(str(exc))
            return result
        fetch_results[0].source_name = single_source_name or "manual"
        fetch_results[0].source_type = single_source_type or "party_official"
        if supplemental_urls:
            _append_supplemental_urls(
                fetch_results[0],
                supplemental_urls,
                progress_callback,
            )
    elif url_sources:
        _emit(
            progress_callback,
            "info",
            f"[pipeline] URL リストモード: {len(url_sources)} 件",
        )
        fetch_results = []
        for ms in url_sources:
            try:
                _emit(progress_callback, "info", f"[pipeline] URL 取得開始: {ms.url}")
                _media_type = detect_url_media_type(ms.url)
                if _media_type == "pdf":
                    _emit(progress_callback, "info", "[pdf] ページ解析中...")
                elif _media_type == "youtube":
                    _emit(progress_callback, "info", "[youtube] 字幕取得中...")
                fr = _fetch_single_url(ms.url)
                fr.source_name = ms.source_name
                fr.source_type = ms.source_type
                fetch_results.append(fr)
                _emit(
                    progress_callback,
                    "info",
                    f"[pipeline] URL 取得成功: {ms.url} ({len(fr.body_text)} 文字)",
                )
            except ValueError as exc:
                msg = f"[pipeline] テキスト抽出に失敗しました: {ms.url} — {exc}"
                _emit(progress_callback, "error", msg)
                result.errors.append(msg)
            except Exception as exc:
                msg = f"[pipeline] URL 取得失敗: {ms.url} — {exc}"
                _emit(progress_callback, "error", msg)
                result.errors.append(msg)
    else:
        fetch_results = fetch_articles_from_feeds(feeds)
        for fetch_result in fetch_results:
            _append_auto_supplemental_pdfs(fetch_result, progress_callback)
    result.total_fetched = len(fetch_results)
    _emit(
        progress_callback,
        "info",
        f"[pipeline] フェッチ完了: {result.total_fetched} 件",
    )

    # 2. fetch_only モードはフェッチ結果を表示して終了する
    if fetch_only:
        for i, r in enumerate(fetch_results, 1):
            _emit(
                progress_callback,
                "info",
                f"[fetch-only] {i:>3}. [{r.source_name}] {r.title}\n"
                f"             URL: {r.source_url}\n"
                f"             公開日: {r.published_at}\n"
                f"             本文長: {len(r.body_text)} 文字",
            )
        _emit(
            progress_callback,
            "info",
            f"[pipeline] fetch-only 完了: {result.total_fetched} 件",
        )
        return result

    # 3. scraper_max_items_per_run を超えないよう上限を適用する
    if len(fetch_results) > settings.scraper_max_items_per_run:
        _emit(
            progress_callback,
            "info",
            "[pipeline] 上限適用: "
            f"{len(fetch_results)} → {settings.scraper_max_items_per_run} 件",
        )
        fetch_results = fetch_results[: settings.scraper_max_items_per_run]

    for fetch_result in fetch_results:
        # 重複チェック: 正規化済み URL が DB に存在する場合はスキップする
        normalized_url = _normalize_url(fetch_result.source_url)
        fetch_result.source_url = normalized_url
        from app.infrastructure.db.models import Article as ArticleModel
        from app.infrastructure.db.session import SessionLocal as _SessionLocal
        _dup_session = _SessionLocal()
        try:
            exists = _dup_session.query(ArticleModel).filter(
                ArticleModel.primary_source_url == normalized_url
            ).first()
        finally:
            _dup_session.close()
        if exists:
            _emit(
                progress_callback,
                "info",
                f"[pipeline] スキップ（重複URL）: {normalized_url}",
            )
            result.total_skipped += 1
            continue

        # 4. 本文が短い場合は URL からフル本文を取得して補強する（HTML のみ）
        if (
            fetch_result.media_type == "html"
            and len(fetch_result.body_text) < _MIN_BODY_LENGTH
        ):
            try:
                _emit(
                    progress_callback,
                    "info",
                    f"[pipeline] 本文補強開始: {fetch_result.source_url}",
                )
                full_text = fetch_article_text(fetch_result.source_url)
                if full_text:
                    fetch_result.body_text = full_text
                    _emit(
                        progress_callback,
                        "info",
                        "[pipeline] 本文補強成功: "
                        f"{len(full_text)} 文字 {fetch_result.source_url}",
                    )
            except Exception as exc:
                _emit(
                    progress_callback, "warning",
                    "[pipeline] 本文補強失敗（継続）: "
                    f"{fetch_result.source_url} — {exc}",
                )

        # 5. LLM で処理する（エラー時は None が返る）
        _emit(
            progress_callback,
            "info",
            f"[pipeline] LLM 処理開始: {fetch_result.source_url}",
        )
        llm_output = process_article_with_llm(fetch_result)
        if llm_output is None:
            msg = f"[pipeline] LLM 処理失敗: {fetch_result.source_url}"
            _emit(progress_callback, "error", msg)
            result.errors.append(msg)
            continue
        result.total_processed += 1
        _emit(
            progress_callback,
            "info",
            f"[pipeline] LLM 処理成功: {llm_output.display_title}",
        )

        if dry_run:
            _emit(
                progress_callback,
                "info",
                f"[pipeline] dry_run: {llm_output.display_title}",
            )
            continue

        # 6. DB に保存する（セッションは 1 記事ごとに commit / rollback する）
        session = SessionLocal()
        try:
            article_id = save_article(session, fetch_result, llm_output)
            session.commit()
            result.total_saved += 1
            result.saved_article_ids.append(article_id)
            _emit(progress_callback, "info", f"[pipeline] 保存完了: {article_id}")
        except Exception as exc:
            session.rollback()
            msg = f"[pipeline] DB 保存失敗: {fetch_result.source_url} — {exc}"
            _emit(progress_callback, "error", msg)
            result.errors.append(msg)
        finally:
            session.close()

    _emit(
        progress_callback, "info",
        f"[pipeline] 完了: fetch={result.total_fetched}, "
        f"skipped={result.total_skipped}, "
        f"processed={result.total_processed}, saved={result.total_saved}, "
        f"errors={len(result.errors)}",
    )
    return result
