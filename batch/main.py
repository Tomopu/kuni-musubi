"""batch 実行エントリポイント。

使い方（batch/ ディレクトリから実行）:
    PYTHONPATH=..:../backend uv run python -m batch.main                          # 通常実行
    PYTHONPATH=..:../backend uv run python -m batch.main --fetch-only             # フェッチのみ
    PYTHONPATH=..:../backend uv run python -m batch.main --dry-run                # LLM まで、DB なし
    PYTHONPATH=..:../backend uv run python -m batch.main --url "https://..."      # URL 指定 1件処理
    PYTHONPATH=..:../backend uv run python -m batch.main --url-list config/manual_sources.yml  # URL リスト処理
    PYTHONPATH=..:../backend uv run python -m batch.main --fetch-only --party "公明党"  # 特定政党のみ
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
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="指定した URL 1件のみを処理する（RSS フェッチをスキップ）",
    )
    parser.add_argument(
        "--url-list",
        type=str,
        default=None,
        dest="url_list",
        help="YAML ファイルに記載された複数 URL を処理する（sources[].url, source_name, source_type）",
    )
    parser.add_argument(
        "--party",
        type=str,
        default=None,
        metavar="PARTY_NAME",
        help="指定した政党名のフィードのみを処理する（例: --party 公明党）",
    )
    args = parser.parse_args()

    # URL リスト YAML を読み込む
    url_sources = None
    if args.url_list:
        import yaml
        from batch.steps.fetch import ManualSource
        with open(args.url_list, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        url_sources = [
            ManualSource(
                url=s["url"],
                source_name=s.get("source_name", "manual"),
                source_type=s.get("source_type", "party_official"),
            )
            for s in data.get("sources", [])
            if s.get("url")
        ]
        print(f"[main] URL リスト読み込み: {len(url_sources)} 件 ({args.url_list})")

    # --party フィルタ: 特定政党のフィードのみに絞り込む
    feeds = None
    if args.party and not args.url and not args.url_list:
        from batch.steps.fetch import load_feeds_from_config
        all_feeds = load_feeds_from_config()
        feeds = [f for f in all_feeds if f.source_name == args.party]
        if not feeds:
            print(f"[main] 政党 '{args.party}' のフィードが parties.yml に見つかりません")
            return
        print(f"[main] 政党フィルタ: '{args.party}' ({len(feeds)} エントリ)")

    result = run_article_pipeline(
        feeds=feeds,
        dry_run=args.dry_run,
        fetch_only=args.fetch_only,
        single_url=args.url,
        url_sources=url_sources,
    )

    if result.errors:
        print(f"\n[main] エラー {len(result.errors)} 件:")
        for err in result.errors:
            print(f"  {err}")


if __name__ == "__main__":
    main()
