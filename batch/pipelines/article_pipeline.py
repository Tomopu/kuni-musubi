"""記事収集パイプライン。

RSS フィードを取得 → LLM 処理 → DB 保存の一連のフローを実行する。
"""

import uuid
from dataclasses import dataclass, field

from batch.db.session import SessionLocal
from batch.scrapers.html_parser import fetch_article_text
from batch.settings import settings
from batch.steps.fetch import (
    FeedConfig,
    FetchResult,
    fetch_articles_from_feeds,
    load_feeds_from_config,
)
from batch.steps.llm_process import process_article_with_llm
from batch.steps.save import save_article

# この文字数未満の本文は URL からフル本文を取得して補強する
_MIN_BODY_LENGTH = 300


@dataclass
class PipelineResult:
    """パイプライン実行結果のサマリ。"""

    total_fetched: int = 0
    total_processed: int = 0
    total_saved: int = 0
    saved_article_ids: list[uuid.UUID] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def run_article_pipeline(
    feeds: list[FeedConfig] | None = None,
    dry_run: bool = False,
    fetch_only: bool = False,
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
        fetch_only: True のときは LLM 処理・DB 保存をスキップしてフェッチ結果のみ表示する。

    Returns:
        PipelineResult: 実行結果サマリ。
    """
    result = PipelineResult()
    if feeds is None:
        feeds = load_feeds_from_config()

    # 1. RSS フィードから記事を取得する
    fetch_results: list[FetchResult] = fetch_articles_from_feeds(feeds)
    result.total_fetched = len(fetch_results)
    print(f"[pipeline] フェッチ完了: {result.total_fetched} 件")

    # 2. fetch_only モードはフェッチ結果を表示して終了する
    if fetch_only:
        for i, r in enumerate(fetch_results, 1):
            print(f"[fetch-only] {i:>3}. [{r.source_name}] {r.title}")
            print(f"             URL: {r.source_url}")
            print(f"             公開日: {r.published_at}")
            print(f"             本文長: {len(r.body_text)} 文字")
        print(f"[pipeline] fetch-only 完了: {result.total_fetched} 件")
        return result

    # 3. scraper_max_items_per_run を超えないよう上限を適用する
    if len(fetch_results) > settings.scraper_max_items_per_run:
        print(
            f"[pipeline] 上限適用: {len(fetch_results)} → {settings.scraper_max_items_per_run} 件"
        )
        fetch_results = fetch_results[: settings.scraper_max_items_per_run]

    for fetch_result in fetch_results:
        # 4. 本文が短い場合は URL からフル本文を取得して補強する
        if len(fetch_result.body_text) < _MIN_BODY_LENGTH:
            try:
                full_text = fetch_article_text(fetch_result.source_url)
                if full_text:
                    fetch_result.body_text = full_text
                    print(
                        f"[pipeline] 本文補強: {len(full_text)} 文字"
                        f" {fetch_result.source_url}"
                    )
            except Exception as exc:
                print(
                    f"[pipeline] 本文補強失敗（継続）:"
                    f" {fetch_result.source_url} — {exc}"
                )

        # 5. LLM で処理する（エラー時は None が返る）
        llm_output = process_article_with_llm(fetch_result)
        if llm_output is None:
            msg = f"[pipeline] LLM 処理失敗: {fetch_result.source_url}"
            result.errors.append(msg)
            continue
        result.total_processed += 1

        if dry_run:
            print(f"[pipeline] dry_run: {llm_output.display_title}")
            continue

        # 6. DB に保存する（セッションは 1 記事ごとに commit / rollback する）
        session = SessionLocal()
        try:
            article_id = save_article(session, fetch_result, llm_output)
            session.commit()
            result.total_saved += 1
            result.saved_article_ids.append(article_id)
            print(f"[pipeline] 保存完了: {article_id}")
        except Exception as exc:
            session.rollback()
            msg = f"[pipeline] DB 保存失敗: {fetch_result.source_url} — {exc}"
            print(msg)
            result.errors.append(msg)
        finally:
            session.close()

    print(
        f"[pipeline] 完了: fetch={result.total_fetched}, "
        f"processed={result.total_processed}, saved={result.total_saved}, "
        f"errors={len(result.errors)}"
    )
    return result
