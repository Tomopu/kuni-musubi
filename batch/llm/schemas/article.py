"""LLM が出力する記事処理結果の Pydantic スキーマ。

docs/technical/20260501_LLM出力スキーマ設計.md に基づく。
"""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

# relation_type の許容値
RelationType = Literal["primary", "mentioned", "opposition_view"]

# source_type の許容値
SourceType = Literal[
    "party_official", "government", "local_government", "news_media", "other"
]


class GroundingSource(BaseModel):
    """Google 検索グラウンディングで参照した出典 URL。"""

    url: str = Field(..., min_length=1)
    title: str = ""
    source_type: SourceType = "other"

    @field_validator("url")
    @classmethod
    def validate_url_scheme(cls, v: str) -> str:
        """javascript: スキームを禁止する（XSS 対策）。"""
        if v.lower().strip().startswith("javascript:"):
            raise ValueError("javascript: URL は禁止されています")
        return v


class RelatedParty(BaseModel):
    """記事に関連する政党情報。"""

    party_name: str = Field(..., min_length=1, max_length=100)
    party_short_name: str = Field(..., min_length=1, max_length=20)
    relation_type: RelationType


class SourceSummary(BaseModel):
    """一次情報ソースのサマリ。"""

    primary_source_url: str = Field(..., min_length=1)
    source_type: SourceType = "party_official"
    source_name: str = ""
    published_at: str = ""

    @field_validator("primary_source_url")
    @classmethod
    def validate_url_scheme(cls, v: str) -> str:
        """javascript: スキームを禁止する（XSS 対策）。"""
        lower = v.lower().strip()
        if lower.startswith("javascript:"):
            raise ValueError("javascript: URL は禁止されています")
        return v


class QualityFlags(BaseModel):
    """LLM 出力の品質・レビュー要否フラグ。"""

    is_positive_news: bool = True
    is_solution_oriented: bool = True
    needs_human_review: bool = False
    risk_notes: list[str] = Field(default_factory=list)


class ArticleLLMOutput(BaseModel):
    """記事処理 LLM の出力スキーマ（完全版）。

    バッチ処理で生成し、article_display_contents テーブルに保存する。
    """

    display_title: str = Field(..., min_length=1, max_length=300)
    card_summary: str = Field(..., min_length=1, max_length=400)
    related_parties: list[RelatedParty] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    positive_point: str = Field(..., min_length=1)
    life_impact: str = Field(..., min_length=1)
    remaining_issues: list[str] = Field(default_factory=list)
    public_reactions_summary: str = ""
    grounding_sources: list[GroundingSource] = Field(default_factory=list)
    source_summary: SourceSummary
    quality_flags: QualityFlags = Field(default_factory=QualityFlags)

    @field_validator("categories")
    @classmethod
    def limit_categories(cls, v: list[str]) -> list[str]:
        """カテゴリは最大 10 件。"""
        return v[:10]

    @field_validator("related_parties")
    @classmethod
    def require_primary_party(cls, v: list[RelatedParty]) -> list[RelatedParty]:
        """primary な政党が少なくとも 1 件あることを推奨（警告ではなく通過）。"""
        # MVP では強制せず、quality_flags.needs_human_review で運用する。
        return v
