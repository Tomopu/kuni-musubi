"""URL リスト取り込みのテスト。"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml

from batch.steps.fetch import ManualSource


class TestManualSource:
    """ManualSource データクラスのテスト。"""

    def test_default_values(self) -> None:
        ms = ManualSource(url="https://example.com/news/1")
        assert ms.url == "https://example.com/news/1"
        assert ms.source_name == "manual"
        assert ms.source_type == "party_official"

    def test_custom_values(self) -> None:
        ms = ManualSource(
            url="https://example.com/news/1",
            source_name="自由民主党",
            source_type="party_official",
        )
        assert ms.source_name == "自由民主党"
        assert ms.source_type == "party_official"


class TestUrlListYamlParsing:
    """URL リスト YAML の読み込みテスト。"""

    def test_parse_valid_yaml(self) -> None:
        """有効な YAML を読み込んで ManualSource リストを生成できる。"""
        data = {
            "sources": [
                {"url": "https://example.com/news/1", "source_name": "自民党", "source_type": "party_official"},
                {"url": "https://example.com/news/2", "source_name": "立憲", "source_type": "party_official"},
            ]
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False, encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True)
            tmp_path = f.name

        with open(tmp_path, encoding="utf-8") as f:
            loaded = yaml.safe_load(f)

        sources = [
            ManualSource(
                url=s["url"],
                source_name=s.get("source_name", "manual"),
                source_type=s.get("source_type", "party_official"),
            )
            for s in loaded.get("sources", [])
            if s.get("url")
        ]

        assert len(sources) == 2
        assert sources[0].url == "https://example.com/news/1"
        assert sources[0].source_name == "自民党"
        assert sources[1].url == "https://example.com/news/2"

    def test_example_yml_is_valid(self) -> None:
        """manual_sources.example.yml が有効な YAML として読み込める。"""
        example_path = Path(__file__).parent.parent / "config" / "manual_sources.example.yml"
        assert example_path.exists(), "manual_sources.example.yml が存在しません"
        with open(example_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert "sources" in data
        assert isinstance(data["sources"], list)
        for s in data["sources"]:
            assert "url" in s

    def test_empty_sources_returns_empty_list(self) -> None:
        """sources が空の場合は空リストを返す。"""
        data = {"sources": []}
        sources = [
            ManualSource(url=s["url"])
            for s in data.get("sources", [])
            if s.get("url")
        ]
        assert len(sources) == 0

    def test_entry_without_url_is_skipped(self) -> None:
        """url キーのないエントリはスキップされる。"""
        data = {
            "sources": [
                {"source_name": "テスト"},  # url なし
                {"url": "https://example.com/news/1"},
            ]
        }
        sources = [
            ManualSource(url=s["url"])
            for s in data.get("sources", [])
            if s.get("url")
        ]
        assert len(sources) == 1
        assert sources[0].url == "https://example.com/news/1"


class TestPipelineWithUrlSources:
    """pipeline の url_sources パラメータのテスト。"""

    def test_url_sources_skips_feed_fetch(self) -> None:
        """url_sources が指定された場合、フィードフェッチをスキップする。"""
        from batch.pipelines.article_pipeline import run_article_pipeline

        url_sources = [ManualSource(url="https://example.com/news/test")]

        with (
            patch("batch.pipelines.article_pipeline.fetch_articles_from_feeds") as mock_feeds,
            patch("batch.pipelines.article_pipeline._fetch_single_url") as mock_fetch,
            patch("batch.pipelines.article_pipeline.process_article_with_llm", return_value=None),
        ):
            mock_fetch.return_value = MagicMock(
                title="テスト記事",
                source_url="https://example.com/news/test",
                source_name="manual",
                source_type="party_official",
                published_at="2026-05-09T00:00:00+00:00",
                body_text="テスト本文" * 100,
                feed_url="https://example.com/news/test",
            )
            with patch("batch.pipelines.article_pipeline.fetch_article_text"), \
                 patch("app.infrastructure.db.session.SessionLocal") as mock_session_cls:
                mock_session = MagicMock()
                mock_session_cls.return_value = mock_session
                mock_session.query.return_value.filter.return_value.first.return_value = None

                result = run_article_pipeline(
                    url_sources=url_sources,
                    fetch_only=True,
                )

        # フィードフェッチは呼ばれない
        mock_feeds.assert_not_called()
        # URL フェッチは呼ばれる
        mock_fetch.assert_called_once_with("https://example.com/news/test")
        assert result.total_fetched == 1

    def test_duplicate_url_is_skipped(self) -> None:
        """DB に既存の URL はスキップされ total_skipped がインクリメントされる。"""
        from batch.pipelines.article_pipeline import run_article_pipeline

        url_sources = [ManualSource(url="https://example.com/news/existing")]

        with (
            patch("batch.pipelines.article_pipeline._fetch_single_url") as mock_fetch,
            patch("batch.pipelines.article_pipeline.process_article_with_llm") as mock_llm,
        ):
            mock_fetch.return_value = MagicMock(
                source_url="https://example.com/news/existing",
                body_text="テスト本文",
            )

            with patch("batch.pipelines.article_pipeline.fetch_article_text"), \
                 patch("app.infrastructure.db.session.SessionLocal") as mock_session_cls:
                mock_session = MagicMock()
                mock_session_cls.return_value = mock_session
                # DB に既存レコードがある（重複）
                mock_session.query.return_value.filter.return_value.first.return_value = MagicMock()

                result = run_article_pipeline(url_sources=url_sources)

        mock_llm.assert_not_called()
        assert result.total_skipped == 1
        assert result.total_saved == 0

    def test_progress_callback_is_called(self) -> None:
        """progress_callback が適切に呼ばれる。"""
        from batch.pipelines.article_pipeline import PipelineEvent, run_article_pipeline

        events: list[PipelineEvent] = []

        def callback(event: PipelineEvent) -> None:
            events.append(event)

        url_sources = [ManualSource(url="https://example.com/news/1")]

        with (
            patch("batch.pipelines.article_pipeline._fetch_single_url") as mock_fetch,
            patch("batch.pipelines.article_pipeline.process_article_with_llm", return_value=None),
        ):
            mock_fetch.return_value = MagicMock(
                source_url="https://example.com/news/1",
                body_text="テスト本文",
            )
            with patch("batch.pipelines.article_pipeline.fetch_article_text"), \
                 patch("app.infrastructure.db.session.SessionLocal") as mock_session_cls:
                mock_session = MagicMock()
                mock_session_cls.return_value = mock_session
                mock_session.query.return_value.filter.return_value.first.return_value = None

                run_article_pipeline(url_sources=url_sources, progress_callback=callback)

        assert len(events) > 0
        messages = [e.message for e in events]
        assert any("URL リストモード" in m for m in messages)

    def test_single_body_text_skips_url_fetch(self) -> None:
        """本文直接入力がある場合、単一 URL の本文取得をスキップする。"""
        from batch.pipelines.article_pipeline import PipelineEvent, run_article_pipeline

        events: list[PipelineEvent] = []

        def callback(event: PipelineEvent) -> None:
            events.append(event)

        with patch("batch.pipelines.article_pipeline._fetch_single_url") as mock_fetch:
            result = run_article_pipeline(
                single_url="https://www.youtube.com/watch?v=test",
                single_source_name="手動入力",
                single_source_type="party_official",
                single_body_text="これは管理画面から直接入力した本文です。",
                fetch_only=True,
                progress_callback=callback,
            )

        mock_fetch.assert_not_called()
        assert result.total_fetched == 1
        messages = [e.message for e in events]
        assert any("本文直接入力を使用します" in m for m in messages)
