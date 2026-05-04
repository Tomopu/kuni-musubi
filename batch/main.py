"""batch 実行エントリポイント。

使い方:
    python -m batch.main              # デフォルトフィードで実行
    python -m batch.main --dry-run    # DB 保存なしで動作確認
"""

import argparse

from batch.pipelines.article_pipeline import run_article_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Kuni-Musubi 記事収集バッチ")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="DB 保存をスキップして動作確認のみ行う",
    )
    args = parser.parse_args()

    result = run_article_pipeline(dry_run=args.dry_run)

    if result.errors:
        print(f"\n[main] エラー {len(result.errors)} 件:")
        for err in result.errors:
            print(f"  {err}")


if __name__ == "__main__":
    main()
