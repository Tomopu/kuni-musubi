"""管理画面からのバッチ取り込みを管理するサービス層。

バックグラウンドスレッドでパイプラインを実行し、進捗を import_job_logs に記録する。
"""

import json
import os
import sys
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.infrastructure.db.models import ImportJob, ImportJobLog
from app.infrastructure.db.session import SessionLocal


def _ensure_batch_import_path() -> None:
    """backend 直起動でも batch パッケージを import できるようにする。"""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "batch").is_dir():
            path = str(parent)
            if path not in sys.path:
                sys.path.insert(0, path)
            return


@dataclass
class JobParams:
    """ジョブ実行パラメータ。"""

    job_type: str  # full | fetch_only | dry_run | single_url | url_list
    party_name: str | None = None
    single_url: str | None = None
    single_source_name: str = "manual"
    single_source_type: str = "party_official"
    supplemental_urls: list[str] | None = None
    url_sources: list[dict[str, str]] | None = None
    dry_run: bool = False
    fetch_only: bool = False


def has_gemini_key() -> bool:
    """GEMINI_API_KEY が環境変数またはバッチ設定に存在するか確認する。"""
    return bool(os.environ.get("GEMINI_API_KEY", ""))


def list_import_party_names() -> list[str]:
    """parties.yml に定義された取り込み対象政党名を重複なしで返す。"""
    try:
        _ensure_batch_import_path()
        from batch.steps.fetch import load_feeds_from_config

        names: list[str] = []
        seen: set[str] = set()
        for feed in load_feeds_from_config():
            if feed.source_name in seen:
                continue
            names.append(feed.source_name)
            seen.add(feed.source_name)
        return names
    except Exception:
        return []


def get_active_job(db: Any) -> "ImportJob | None":
    """実行中（queued/running）のジョブを返す。なければ None。"""
    return (
        db.query(ImportJob)
        .filter(ImportJob.status.in_(["queued", "running"]))
        .first()
    )


def recover_stale_jobs() -> int:
    """起動時に running 状態で残っているジョブを failed にリカバリする。

    プロセスクラッシュ等で DB に残ったゾンビジョブを全件 failed に更新し、
    ログを記録する。

    Returns:
        リカバリしたジョブ数
    """
    session = SessionLocal()
    count = 0
    try:
        stale_jobs = (
            session.query(ImportJob)
            .filter(ImportJob.status == "running")
            .all()
        )
        for job in stale_jobs:
            job.status = "failed"
            job.finished_at = datetime.now(timezone.utc)
            log = ImportJobLog(
                id=uuid.uuid4(),
                job_id=job.id,
                level="error",
                message="サーバーの再起動などによりプロセスが中断されました",
            )
            session.add(log)
            count += 1
        if count:
            session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()
    return count


def create_and_start_job(params: JobParams) -> uuid.UUID:
    """ジョブレコードを作成してバックグラウンドスレッドで実行を開始する。

    1. import_jobs にレコードを作成する
    2. デーモンスレッドで _run_job を起動する
    3. job_id を返す
    """
    # 1. ジョブレコードを作成する
    session = SessionLocal()
    try:
        job = ImportJob(
            id=uuid.uuid4(),
            job_type=params.job_type,
            status="queued",
            params=json.dumps({
                "party_name": params.party_name,
                "single_url": params.single_url,
                "single_source_name": params.single_source_name,
                "single_source_type": params.single_source_type,
                "supplemental_urls": params.supplemental_urls,
                "url_sources": params.url_sources,
                "dry_run": params.dry_run,
                "fetch_only": params.fetch_only,
            }),
        )
        session.add(job)
        session.commit()
        job_id = job.id
    finally:
        session.close()

    # 2. バックグラウンドスレッドで実行する
    t = threading.Thread(target=_run_job, args=(job_id, params), daemon=True)
    t.start()
    return job_id


def _write_log(
    job_id: uuid.UUID,
    level: str,
    message: str,
    metadata: dict | None = None,
) -> None:
    """import_job_logs に1件書き込む（専用セッションを開閉する）。"""
    session = SessionLocal()
    try:
        log = ImportJobLog(
            id=uuid.uuid4(),
            job_id=job_id,
            level=level,
            message=message,
            log_metadata=json.dumps(metadata, ensure_ascii=False) if metadata else None,
        )
        session.add(log)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()


def _update_job_status(job_id: uuid.UUID, status: str, result: Any = None) -> None:
    """ジョブのステータスと集計値を更新する（専用セッションを開閉する）。"""
    session = SessionLocal()
    try:
        job = session.query(ImportJob).filter(ImportJob.id == job_id).first()
        if not job:
            return
        job.status = status
        job.finished_at = datetime.now(timezone.utc)
        if result is not None:
            job.total_fetched = result.total_fetched
            job.total_processed = result.total_processed
            job.total_saved = result.total_saved
            job.total_skipped_duplicates = result.total_skipped
            job.total_errors = len(result.errors)
            job.saved_article_ids = [str(aid) for aid in result.saved_article_ids]
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()


def _run_job(job_id: uuid.UUID, params: JobParams) -> None:
    """バックグラウンドスレッドでパイプラインを実行する。

    1. ステータスを running に更新する
    2. コールバック経由で進捗ログを import_job_logs に書き込む
    3. パイプラインを実行する
    4. 結果でジョブを更新する
    """
    # 1. ステータスを running に更新する
    session = SessionLocal()
    try:
        job = session.query(ImportJob).filter(ImportJob.id == job_id).first()
        if not job:
            return
        job.status = "running"
        job.started_at = datetime.now(timezone.utc)
        session.commit()
    finally:
        session.close()

    try:
        _ensure_batch_import_path()

        # 2. 進捗ログ書き込みコールバックを定義する
        from batch.pipelines.article_pipeline import PipelineEvent

        def callback(event: PipelineEvent) -> None:
            _write_log(job_id, event.level, event.message)

        # 3. パイプラインを実行する
        from batch.pipelines.article_pipeline import run_article_pipeline
        from batch.steps.fetch import ManualSource, load_feeds_from_config

        url_sources = None
        if params.url_sources:
            url_sources = [
                ManualSource(
                    url=s["url"],
                    source_name=s.get("source_name", "manual"),
                    source_type=s.get("source_type", "party_official"),
                )
                for s in params.url_sources
                if s.get("url")
            ]

        feeds = None
        if params.party_name and not params.single_url and not url_sources:
            all_feeds = load_feeds_from_config()
            feeds = [
                feed
                for feed in all_feeds
                if feed.source_name == params.party_name
            ]
            if not feeds:
                raise ValueError(
                    f"政党 '{params.party_name}' のフィードが "
                    "parties.yml に見つかりません"
                )
            _write_log(
                job_id,
                "info",
                f"政党フィルタ: {params.party_name} ({len(feeds)} 件)",
            )

        result = run_article_pipeline(
            feeds=feeds,
            dry_run=params.dry_run,
            fetch_only=params.fetch_only,
            single_url=params.single_url,
            single_source_name=params.single_source_name,
            single_source_type=params.single_source_type,
            supplemental_urls=params.supplemental_urls,
            url_sources=url_sources,
            progress_callback=callback,
        )

        # 4. 結果でジョブを更新する
        _update_job_status(job_id, "completed", result)

    except Exception as exc:
        _write_log(job_id, "error", f"パイプライン実行エラー: {exc}")
        _update_job_status(job_id, "failed")
