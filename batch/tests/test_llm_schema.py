"""LLM 出力スキーマ（ArticleLLMOutput）のバリデーションテスト。

CLAUDE.md の Testing 方針: LLM 出力 schema validation テストを優先する。
"""

# ruff: noqa: E501

import pytest
from pydantic import ValidationError

from batch.llm.schemas.article import (
    ArticleLLMOutput,
    SourceSummary,
)

# 最小限の有効なペイロード
VALID_PAYLOAD: dict = {
    "display_title": "子育て支援が拡充、月5万円補助が現実へ",
    "card_summary": "政府は2024年度から月5万円の子育て支援補助を段階的に拡充する方針を発表した。",
    "related_parties": [
        {
            "party_name": "自由民主党",
            "party_short_name": "自民党",
            "relation_type": "primary",
        }
    ],
    "categories": ["子育て", "社会保障"],
    "positive_point": "長年課題だった子育て支援の予算が増額され、具体的な補助額が示された。",
    "life_impact": "0〜3歳の子を持つ家庭は月5万円の補助が受けられる見込み。保育料の実質負担が軽減される。",
    "remaining_issues": ["財源の確保方法が未確定", "所得制限の有無が不明"],
    "public_reactions_summary": {
        "government_or_ruling_party_view": "子育て世代の負担軽減に向けた重要な一歩と評価",
        "opposition_view": "財源の裏付けが不明確として慎重な議論を求める声",
        "public_opinion_or_expert_view": "子育て世代からは歓迎の声、専門家からは制度設計の精査を求める意見",
    },
    "source_summary": {
        "primary_source_url": "https://example.com/article/1",
        "source_type": "party_official",
        "source_name": "自民党公式サイト",
        "published_at": "2024-01-15T10:00:00+09:00",
    },
    "quality_flags": {
        "is_positive_news": True,
        "is_solution_oriented": True,
        "needs_human_review": False,
        "risk_notes": [],
    },
}


class TestArticleLLMOutputValid:
    def test_full_valid_payload(self) -> None:
        """完全な有効ペイロードが検証を通過する。"""
        output = ArticleLLMOutput.model_validate(VALID_PAYLOAD)
        assert output.display_title == "子育て支援が拡充、月5万円補助が現実へ"
        assert len(output.related_parties) == 1
        assert output.related_parties[0].relation_type == "primary"
        assert len(output.categories) == 2
        assert output.quality_flags.needs_human_review is False

    def test_minimal_payload_with_defaults(self) -> None:
        """related_parties・categories・remaining_issues が空でも通過する。"""
        payload = {
            "display_title": "テストタイトル",
            "card_summary": "テスト要約",
            "positive_point": "良い点",
            "life_impact": "生活への影響",
            "source_summary": {
                "primary_source_url": "https://example.com",
            },
        }
        output = ArticleLLMOutput.model_validate(payload)
        assert output.related_parties == []
        assert output.categories == []
        assert output.remaining_issues == []
        assert output.quality_flags.is_positive_news is True

    def test_needs_human_review_true(self) -> None:
        """needs_human_review=True が設定できる。"""
        payload = {**VALID_PAYLOAD, "quality_flags": {**VALID_PAYLOAD["quality_flags"], "needs_human_review": True}}
        output = ArticleLLMOutput.model_validate(payload)
        assert output.quality_flags.needs_human_review is True


class TestArticleLLMOutputInvalid:
    def test_missing_display_title(self) -> None:
        """display_title がない場合は ValidationError。"""
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "display_title"}
        with pytest.raises(ValidationError):
            ArticleLLMOutput.model_validate(payload)

    def test_empty_display_title(self) -> None:
        """display_title が空文字の場合は ValidationError。"""
        payload = {**VALID_PAYLOAD, "display_title": ""}
        with pytest.raises(ValidationError):
            ArticleLLMOutput.model_validate(payload)

    def test_missing_card_summary(self) -> None:
        """card_summary がない場合は ValidationError。"""
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "card_summary"}
        with pytest.raises(ValidationError):
            ArticleLLMOutput.model_validate(payload)

    def test_missing_source_summary(self) -> None:
        """source_summary がない場合は ValidationError。"""
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "source_summary"}
        with pytest.raises(ValidationError):
            ArticleLLMOutput.model_validate(payload)

    def test_invalid_relation_type(self) -> None:
        """invalid な relation_type は ValidationError。"""
        payload = {
            **VALID_PAYLOAD,
            "related_parties": [
                {
                    "party_name": "自由民主党",
                    "party_short_name": "自民党",
                    "relation_type": "invalid_type",
                }
            ],
        }
        with pytest.raises(ValidationError):
            ArticleLLMOutput.model_validate(payload)

    def test_invalid_source_type(self) -> None:
        """invalid な source_type は ValidationError。"""
        payload = {
            **VALID_PAYLOAD,
            "source_summary": {
                **VALID_PAYLOAD["source_summary"],
                "source_type": "unknown_source",
            },
        }
        with pytest.raises(ValidationError):
            ArticleLLMOutput.model_validate(payload)

    def test_javascript_url_in_source(self) -> None:
        """javascript: URL を含む source_summary は ValidationError。"""
        payload = {
            **VALID_PAYLOAD,
            "source_summary": {
                **VALID_PAYLOAD["source_summary"],
                "primary_source_url": "javascript:alert(1)",
            },
        }
        with pytest.raises(ValidationError):
            ArticleLLMOutput.model_validate(payload)

    def test_display_title_too_long(self) -> None:
        """display_title が 300 文字超は ValidationError。"""
        payload = {**VALID_PAYLOAD, "display_title": "あ" * 301}
        with pytest.raises(ValidationError):
            ArticleLLMOutput.model_validate(payload)


class TestCategoryLimit:
    def test_categories_capped_at_10(self) -> None:
        """カテゴリが 10 件を超えても 10 件に切り詰められる。"""
        payload = {**VALID_PAYLOAD, "categories": [str(i) for i in range(15)]}
        output = ArticleLLMOutput.model_validate(payload)
        assert len(output.categories) == 10


class TestSourceSummaryValidator:
    def test_valid_https_url(self) -> None:
        """https: URL は通過する。"""
        s = SourceSummary(primary_source_url="https://example.com/article")
        assert s.primary_source_url == "https://example.com/article"

    def test_javascript_url_blocked(self) -> None:
        """javascript: URL は ValidationError。"""
        with pytest.raises(ValidationError):
            SourceSummary(primary_source_url="javascript:alert(1)")
