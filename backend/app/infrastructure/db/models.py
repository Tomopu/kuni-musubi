import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# 記事と政党の中間テーブル
article_parties = Table(
    "article_parties",
    Base.metadata,
    Column("article_id", UUID(as_uuid=True), ForeignKey("articles.id"), primary_key=True),
    Column("party_id", UUID(as_uuid=True), ForeignKey("parties.id"), primary_key=True),
    Column("relation_type", String(20), nullable=False, server_default="primary"),
    # primary | mentioned | opposition_view
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=text("now()")),
)

# 記事とカテゴリの中間テーブル
article_categories = Table(
    "article_categories",
    Base.metadata,
    Column("article_id", UUID(as_uuid=True), ForeignKey("articles.id"), primary_key=True),
    Column("category_id", UUID(as_uuid=True), ForeignKey("policy_categories.id"), primary_key=True),
    Column("display_order", Integer, nullable=False, server_default="0"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=text("now()")),
)


class Party(Base):
    __tablename__ = "parties"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    short_name: Mapped[str] = mapped_column(String(20), nullable=False)
    color_hex: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    founded_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    leader_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    house_of_representatives_seats: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    house_of_councillors_seats: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ideology_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    manifesto_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    manifesto_promises: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )
    main_policy_categories: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )
    official_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PolicyCategory(Base):
    __tablename__ = "policy_categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    original_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    primary_source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    collected_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    important_rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    display_content: Mapped["ArticleDisplayContent | None"] = relationship(
        back_populates="article", uselist=False
    )
    sources: Mapped[list["ArticleSource"]] = relationship(back_populates="article")
    parties: Mapped[list["Party"]] = relationship(secondary=article_parties, lazy="select")
    categories: Mapped[list["PolicyCategory"]] = relationship(secondary=article_categories, lazy="select")


class ArticleDisplayContent(Base):
    __tablename__ = "article_display_contents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("articles.id"), nullable=False, unique=True
    )
    display_title: Mapped[str] = mapped_column(String(300), nullable=False)
    card_summary: Mapped[str] = mapped_column(Text, nullable=False)
    thumbnail_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    thumbnail_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    thumbnail_alt_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    positive_point: Mapped[str] = mapped_column(Text, nullable=False)
    life_impact: Mapped[str] = mapped_column(Text, nullable=False)
    remaining_issues: Mapped[str] = mapped_column(Text, nullable=False)
    # 世論・与野党からの評価（JSON 文字列として保存）
    public_reactions_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    article: Mapped["Article"] = relationship(back_populates="display_content")


class ArticleSource(Base):
    __tablename__ = "article_sources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("articles.id"), nullable=False
    )
    source_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    retrieved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    article: Mapped["Article"] = relationship(back_populates="sources")


class OnboardingEvent(Base):
    __tablename__ = "onboarding_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    age_group: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    selected_party_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    selected_party_status: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # none | unknown | skipped | selected
    interest_category_ids: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ArticleEvent(Base):
    __tablename__ = "article_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    surface: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class DailyArticleStat(Base):
    __tablename__ = "daily_article_stats"
    __table_args__ = (UniqueConstraint("article_id", "stat_date"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("articles.id"), nullable=False
    )
    stat_date: Mapped[date] = mapped_column(nullable=False)
    impression_count: Mapped[int] = mapped_column(Integer, default=0)
    card_click_count: Mapped[int] = mapped_column(Integer, default=0)
    detail_view_count: Mapped[int] = mapped_column(Integer, default=0)
    source_click_count: Mapped[int] = mapped_column(Integer, default=0)
    helpful_click_count: Mapped[int] = mapped_column(Integer, default=0)
    unhelpful_click_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class DailyCategoryStat(Base):
    __tablename__ = "daily_category_stats"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("policy_categories.id"), nullable=False
    )
    stat_date: Mapped[date] = mapped_column(nullable=False)
    helpful_click_count: Mapped[int] = mapped_column(Integer, default=0)
    card_click_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
