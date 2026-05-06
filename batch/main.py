"""batch 実行エントリポイント。

使い方（batch/ ディレクトリから実行）:
    PYTHONPATH=..:../backend uv run python -m batch.main                # 通常実行
    PYTHONPATH=..:../backend uv run python -m batch.main --fetch-only   # フェッチのみ
    PYTHONPATH=..:../backend uv run python -m batch.main --dry-run      # LLM まで、DB なし
"""

import argparse

from batch.pipelines.article_pipeline import run_article_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Kuni-Musubi 記事収集バッチ")
    parser.add_argument(
        "--fetch-only",
        action="store_true",
        help="RSS 取得のみ行い LLM 処理・DB 保存をスキップする（スクレイピング動作確認用）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="LLM 処理まで行い DB 保存をスキップする（動作確認用）",
    )
    args = parser.parse_args()

    result = run_article_pipeline(dry_run=args.dry_run, fetch_only=args.fetch_only)

    if result.errors:
        print(f"\n[main] エラー {len(result.errors)} 件:")
        for err in result.errors:
            print(f"  {err}")


if __name__ == "__main__":
    main()
