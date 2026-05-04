"""記事収集パイプライン。

RSS フィードを取得 → LLM 処理 → DB 保存の一連のフローを実行する。
"""

import uuid
from dataclasses import dataclass, field

from batch.db.session import SessionLocal
from batch.steps.fetch import FeedConfig, FetchResult, fetch_articles_from_feeds
from batch.steps.llm_process import process_article_with_llm
from batch.steps.save import save_article

# デフォルトの RSS フィード一覧（MVP の動作確認用）
DEFAULT_FEEDS: list[FeedConfig] = [
    FeedConfig(
        url="https://www.jimin.jp/news/rss/index.xml",
        source_name="自由民主党",
        source_type="party_official",
        max_items=10,
    ),
    FeedConfig(
        url="https://cdp-japan.jp/news/rss",
        source_name="立憲民主党",
        source_type="party_official",
        max_items=10,
    ),
    FeedConfig(
        url="https://www.komei.or.jp/news/rss.xml",
        source_name="公明党",
        source_type="party_official",
        max_items=10,
    ),
]


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
) -> PipelineResult:
    """記事収集パイプラインを実行する。

    1. RSS フィードから記事を取得する
    2. 各記事を LLM で処理する
    3. 処理結果を DB に保存する（dry_run=True のときは保存しない）

    Args:
        feeds: RSS フィード設定リスト。None のときはデフォルトフィードを使う。
        dry_run: True のときは DB 保存をスキップする。

    Returns:
        PipelineResult: 実行結果サマリ。
    """
    result = PipelineResult()
    feeds = feeds or DEFAULT_FEEDS

    # 1. RSS フィードから記事を取得する
    fetch_results: list[FetchResult] = fetch_articles_from_feeds(feeds)
    result.total_fetched = len(fetch_results)
    print(f"[pipeline] フェッチ完了: {result.total_fetched} 件")

    for fetch_result in fetch_results:
        # 2. LLM で処理する
        try:
            llm_output = process_article_with_llm(fetch_result)
            result.total_processed += 1
        except Exception as exc:
            msg = f"[pipeline] LLM 処理失敗: {fetch_result.source_url} — {exc}"
            print(msg)
            result.errors.append(msg)
            continue

        if dry_run:
            print(f"[pipeline] dry_run: {llm_output.display_title}")
            continue

        # 3. DB に保存する（セッションは 1 記事ごとに commit / rollback する）
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
