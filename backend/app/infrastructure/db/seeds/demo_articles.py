# ruff: noqa: E501

import json
import uuid
from datetime import datetime, timezone
from typing import TypedDict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.db.models import (
    Article,
    ArticleDisplayContent,
    ArticleSource,
    article_categories,
    article_parties,
)


class DemoArticleSeed(TypedDict):
    id: uuid.UUID
    party_id: uuid.UUID
    category_ids: list[uuid.UUID]
    display_title: str
    card_summary: str
    thumbnail_text: str
    positive_point: str
    life_impact: str
    remaining_issues: list[str]
    public_reactions_summary: str
    published_at: datetime
    important_rank: int


PARTY = {
    "ldp": uuid.UUID("11111111-0000-0000-0000-000000000001"),
    "cdp": uuid.UUID("11111111-0000-0000-0000-000000000002"),
    "ishin": uuid.UUID("11111111-0000-0000-0000-000000000003"),
    "dpfp": uuid.UUID("11111111-0000-0000-0000-000000000004"),
    "sanseito": uuid.UUID("11111111-0000-0000-0000-000000000005"),
    "jcp": uuid.UUID("11111111-0000-0000-0000-000000000006"),
    "reiwa": uuid.UUID("11111111-0000-0000-0000-000000000007"),
    "sdp": uuid.UUID("11111111-0000-0000-0000-000000000008"),
    "mirai": uuid.UUID("11111111-0000-0000-0000-000000000009"),
}

CATEGORY = {
    "tax": uuid.UUID("22222222-0000-0000-0000-000000000001"),
    "social_security": uuid.UUID("22222222-0000-0000-0000-000000000002"),
    "labor": uuid.UUID("22222222-0000-0000-0000-000000000003"),
    "inflation": uuid.UUID("22222222-0000-0000-0000-000000000004"),
    "childcare": uuid.UUID("22222222-0000-0000-0000-000000000005"),
    "education": uuid.UUID("22222222-0000-0000-0000-000000000006"),
    "defense": uuid.UUID("22222222-0000-0000-0000-000000000007"),
    "diplomacy": uuid.UUID("22222222-0000-0000-0000-000000000008"),
    "energy": uuid.UUID("22222222-0000-0000-0000-000000000010"),
    "regional": uuid.UUID("22222222-0000-0000-0000-000000000011"),
    "environment": uuid.UUID("22222222-0000-0000-0000-000000000014"),
    "disaster": uuid.UUID("22222222-0000-0000-0000-000000000015"),
}

DEMO_ARTICLE_SEEDS: list[DemoArticleSeed] = [
    {
        "id": uuid.UUID("33333333-0000-0000-0000-000000000001"),
        "party_id": PARTY["ldp"],
        "category_ids": [CATEGORY["labor"], CATEGORY["tax"]],
        "display_title": "【デモ】若者の所得向上に向けた支援策を提案",
        "card_summary": "賃上げ支援やキャリア形成を後押しし、若い世代が安心して働ける環境づくりを目指す内容です。",
        "thumbnail_text": "所得向上",
        "positive_point": "若い世代の可処分所得を増やす方向性を示し、働き始めの不安を軽くする政策論点を前に進めています。",
        "life_impact": "賃上げや学び直し支援が広がれば、転職、資格取得、副業など将来の選択肢を増やしやすくなります。",
        "remaining_issues": ["財源をどう確保するか。", "支援が中小企業や地方にも届く設計にできるか。"],
        "public_reactions_summary": "与党内では成長分野への人材移動を後押しする点が評価され、野党からは財源と実効性の説明を求める声があります。",
        "published_at": datetime(2026, 5, 19, 18, 45, tzinfo=timezone.utc),
        "important_rank": 1,
    },
    {
        "id": uuid.UUID("33333333-0000-0000-0000-000000000002"),
        "party_id": PARTY["ldp"],
        "category_ids": [CATEGORY["defense"], CATEGORY["diplomacy"]],
        "display_title": "【デモ】防衛力の抜本的強化に向けた方針を整理",
        "card_summary": "安全保障環境の変化を踏まえ、装備、訓練、国際連携を総合的に強化する方針を示しました。",
        "thumbnail_text": "安全保障",
        "positive_point": "平時から備えを厚くすることで、災害対応や国際協力も含めた安全の基盤づくりにつながります。",
        "life_impact": "防衛・防災体制が整うことで、非常時の情報共有や地域の安心感を高める可能性があります。",
        "remaining_issues": ["防衛費の増加と社会保障など他分野とのバランス。", "国民への説明と透明性の確保。"],
        "public_reactions_summary": "安全保障上の必要性を評価する声がある一方、予算規模や外交努力との両立を求める意見もあります。",
        "published_at": datetime(2026, 5, 16, 12, 20, tzinfo=timezone.utc),
        "important_rank": 3,
    },
    {
        "id": uuid.UUID("33333333-0000-0000-0000-000000000003"),
        "party_id": PARTY["ishin"],
        "category_ids": [CATEGORY["regional"], CATEGORY["education"]],
        "display_title": "【デモ】地方創生2.0で持続可能な地域づくりを推進",
        "card_summary": "行政の効率化、教育環境の充実、地域産業の支援を組み合わせ、地方の魅力を高める提案です。",
        "thumbnail_text": "地方創生",
        "positive_point": "地域ごとの強みを伸ばし、若い世代が住み続けやすい選択肢を広げる視点があります。",
        "life_impact": "通学、子育て、仕事の選択肢が地域内で増えると、都市部に移らなくても暮らしを設計しやすくなります。",
        "remaining_issues": ["人口減少が進む地域で人材をどう確保するか。", "自治体間の格差を広げない運用が必要です。"],
        "public_reactions_summary": "改革志向を評価する声がある一方、地域の実情に合う丁寧な制度設計を求める意見もあります。",
        "published_at": datetime(2026, 5, 18, 16, 10, tzinfo=timezone.utc),
        "important_rank": 4,
    },
    {
        "id": uuid.UUID("33333333-0000-0000-0000-000000000004"),
        "party_id": PARTY["dpfp"],
        "category_ids": [CATEGORY["inflation"], CATEGORY["labor"]],
        "display_title": "【デモ】中小企業向けの賃上げ支援策を拡充",
        "card_summary": "物価高に負けない賃上げを後押しするため、税制や補助制度の活用を提案しています。",
        "thumbnail_text": "賃上げ",
        "positive_point": "賃上げの原資を確保しにくい中小企業に焦点を当て、生活実感に近い課題へ向き合っています。",
        "life_impact": "賃金が上がれば、食費や光熱費の負担感を和らげ、将来への備えもしやすくなります。",
        "remaining_issues": ["支援対象の線引きが複雑になりすぎないか。", "一時的な補助で終わらせず継続的な賃上げにつなげられるか。"],
        "public_reactions_summary": "生活者目線の提案として評価される一方、財源と効果測定の明確化が求められています。",
        "published_at": datetime(2026, 5, 18, 15, 40, tzinfo=timezone.utc),
        "important_rank": 2,
    },
    {
        "id": uuid.UUID("33333333-0000-0000-0000-000000000005"),
        "party_id": PARTY["cdp"],
        "category_ids": [CATEGORY["childcare"], CATEGORY["education"]],
        "display_title": "【デモ】子育てと教育費の負担軽減を提案",
        "card_summary": "給付、学費支援、放課後の居場所づくりを組み合わせ、家庭の負担を軽くする提案です。",
        "thumbnail_text": "子育て",
        "positive_point": "子どもを育てる家庭の不安を具体的に下げ、教育機会を広げる方向性があります。",
        "life_impact": "保育料や教育費の負担が軽くなれば、家計の見通しを立てやすくなります。",
        "remaining_issues": ["所得制限の設計。", "自治体ごとの差をどう埋めるか。"],
        "public_reactions_summary": "子育て世帯から期待がある一方、制度の持続性や財源を問う声もあります。",
        "published_at": datetime(2026, 5, 17, 16, 35, tzinfo=timezone.utc),
        "important_rank": 5,
    },
    {
        "id": uuid.UUID("33333333-0000-0000-0000-000000000006"),
        "party_id": PARTY["jcp"],
        "category_ids": [CATEGORY["inflation"], CATEGORY["social_security"]],
        "display_title": "【デモ】物価高対策の緊急提案を発表",
        "card_summary": "食料品、電気代、社会保障負担に着目し、暮らしを下支えする対策を訴えています。",
        "thumbnail_text": "物価対策",
        "positive_point": "日々の生活費に直結する課題を取り上げ、支援が必要な世帯に光を当てています。",
        "life_impact": "家計支援が届けば、食費や光熱費を切り詰めすぎず生活を守れる可能性があります。",
        "remaining_issues": ["一律支援と重点支援のバランス。", "価格抑制策の副作用をどう抑えるか。"],
        "public_reactions_summary": "生活防衛の観点から評価する声がある一方、経済全体への影響を慎重に見る意見もあります。",
        "published_at": datetime(2026, 5, 16, 10, 30, tzinfo=timezone.utc),
        "important_rank": 6,
    },
    {
        "id": uuid.UUID("33333333-0000-0000-0000-000000000007"),
        "party_id": PARTY["reiwa"],
        "category_ids": [CATEGORY["education"], CATEGORY["childcare"]],
        "display_title": "【デモ】奨学金の負担軽減に向けた新制度を提案",
        "card_summary": "学びたい人が経済状況で進路をあきらめないよう、返済負担の軽減策を示しています。",
        "thumbnail_text": "奨学金",
        "positive_point": "若い世代の学び直しや進学を支えることで、将来の選択肢を広げる狙いがあります。",
        "life_impact": "返済負担が軽くなると、就職後の生活設計や家計の安定につながります。",
        "remaining_issues": ["既存利用者への支援範囲。", "大学や専門学校の質保証との両立。"],
        "public_reactions_summary": "教育機会の平等を重視する声から支持があり、制度の公平性を問う意見もあります。",
        "published_at": datetime(2026, 5, 15, 9, 10, tzinfo=timezone.utc),
        "important_rank": 7,
    },
    {
        "id": uuid.UUID("33333333-0000-0000-0000-000000000008"),
        "party_id": PARTY["sanseito"],
        "category_ids": [CATEGORY["education"], CATEGORY["regional"]],
        "display_title": "【デモ】地域の学びを支える教育環境づくりを提案",
        "card_summary": "地域の特色を生かした教育や、家庭・学校・地域の連携を強める提案です。",
        "thumbnail_text": "地域教育",
        "positive_point": "子どもが身近な地域で多様な経験を得られるよう、学びの場を広げる視点があります。",
        "life_impact": "地域で学びや体験の機会が増えると、家庭だけに負担が偏りにくくなります。",
        "remaining_issues": ["教育内容の中立性。", "地域によって体験機会に差が出ないようにすること。"],
        "public_reactions_summary": "地域参加を評価する声がある一方、公教育との役割分担を丁寧に整理する必要があります。",
        "published_at": datetime(2026, 5, 14, 11, 5, tzinfo=timezone.utc),
        "important_rank": 8,
    },
    {
        "id": uuid.UUID("33333333-0000-0000-0000-000000000009"),
        "party_id": PARTY["sdp"],
        "category_ids": [CATEGORY["disaster"], CATEGORY["social_security"]],
        "display_title": "【デモ】災害時の福祉支援を強化する提案",
        "card_summary": "高齢者や障害のある人が避難しやすい体制づくりを重視した提案です。",
        "thumbnail_text": "防災福祉",
        "positive_point": "災害時に支援が届きにくい人へ目を向け、命と生活を守る仕組みづくりを進めています。",
        "life_impact": "避難所や在宅避難の支援が整うと、家族や地域の不安を減らせます。",
        "remaining_issues": ["平時からの名簿管理とプライバシーの両立。", "自治体職員や支援者の負担軽減。"],
        "public_reactions_summary": "福祉の視点を防災に入れる点が評価され、現場負担への配慮も求められています。",
        "published_at": datetime(2026, 5, 13, 13, 20, tzinfo=timezone.utc),
        "important_rank": 9,
    },
    {
        "id": uuid.UUID("33333333-0000-0000-0000-000000000010"),
        "party_id": PARTY["mirai"],
        "category_ids": [CATEGORY["tax"], CATEGORY["regional"]],
        "display_title": "【デモ】行政手続きのデジタル化で負担を軽減",
        "card_summary": "申請や相談の手間を減らし、誰でも使いやすい行政サービスを目指す提案です。",
        "thumbnail_text": "行政DX",
        "positive_point": "手続きにかかる時間を減らし、生活や仕事に使える時間を増やす方向性があります。",
        "life_impact": "スマートフォンから手続きできる範囲が広がれば、役所へ行く負担を減らせます。",
        "remaining_issues": ["デジタルが苦手な人への支援。", "個人情報保護とセキュリティの徹底。"],
        "public_reactions_summary": "利便性向上への期待がある一方、対面窓口の維持や情報保護を求める声もあります。",
        "published_at": datetime(2026, 5, 12, 12, 15, tzinfo=timezone.utc),
        "important_rank": 10,
    },
]


def _source_url(seed: DemoArticleSeed) -> str:
    return f"https://example.com/kuni-musubi/demo/articles/{seed['id']}"


def _sync_article_display_content(db: Session, article: Article, seed: DemoArticleSeed) -> None:
    display_content = article.display_content
    if display_content is None:
        display_content = ArticleDisplayContent(article_id=seed["id"])
        db.add(display_content)

    display_content.display_title = seed["display_title"]
    display_content.card_summary = seed["card_summary"]
    display_content.thumbnail_type = "text"
    display_content.thumbnail_text = seed["thumbnail_text"]
    display_content.thumbnail_url = None
    display_content.thumbnail_alt_text = f"{seed['thumbnail_text']}のデモ用テキストサムネイル"
    display_content.positive_point = seed["positive_point"]
    display_content.life_impact = seed["life_impact"]
    display_content.remaining_issues = json.dumps(
        seed["remaining_issues"], ensure_ascii=False
    )
    display_content.public_reactions_summary = seed["public_reactions_summary"]
    display_content.created_by = "demo_seed"


def _sync_article_source(db: Session, article_id: uuid.UUID, seed: DemoArticleSeed) -> None:
    existing_source = db.scalars(
        select(ArticleSource).where(
            ArticleSource.article_id == article_id,
            ArticleSource.source_type == "demo",
        )
    ).first()

    source = existing_source or ArticleSource(article_id=article_id)
    if existing_source is None:
        db.add(source)

    source.source_name = "デモ用架空ソース"
    source.source_url = _source_url(seed)
    source.source_type = "demo"
    source.published_at = seed["published_at"]
    source.retrieved_at = seed["published_at"]


def _insert_article_links(db: Session, article_id: uuid.UUID, seed: DemoArticleSeed) -> None:
    existing_party_link = db.execute(
        select(article_parties.c.article_id).where(
            article_parties.c.article_id == article_id,
            article_parties.c.party_id == seed["party_id"],
        )
    ).first()
    if existing_party_link is None:
        db.execute(
            article_parties.insert().values(
                article_id=article_id,
                party_id=seed["party_id"],
                relation_type="primary",
            )
        )

    for order, category_id in enumerate(seed["category_ids"]):
        existing_category_link = db.execute(
            select(article_categories.c.article_id).where(
                article_categories.c.article_id == article_id,
                article_categories.c.category_id == category_id,
            )
        ).first()
        if existing_category_link is None:
            db.execute(
                article_categories.insert().values(
                    article_id=article_id,
                    category_id=category_id,
                    display_order=order,
                )
            )


def seed_demo_articles(db: Session) -> None:
    for seed in DEMO_ARTICLE_SEEDS:
        existing = db.get(Article, seed["id"])
        if existing is not None:
            print(f"  update demo article: {seed['display_title']}")
            existing.original_title = seed["display_title"]
            existing.source_type = "demo"
            existing.primary_source_url = _source_url(seed)
            existing.published_at = seed["published_at"]
            existing.collected_at = seed["published_at"]
            existing.status = "published"
            existing.important_rank = seed["important_rank"]
            existing.is_published = True
            _sync_article_display_content(db, existing, seed)
            _sync_article_source(db, seed["id"], seed)
            _insert_article_links(db, seed["id"], seed)
            continue

        article = Article(
            id=seed["id"],
            original_title=seed["display_title"],
            source_type="demo",
            primary_source_url=_source_url(seed),
            published_at=seed["published_at"],
            collected_at=seed["published_at"],
            status="published",
            important_rank=seed["important_rank"],
            is_published=True,
        )
        db.add(article)
        db.flush()

        _sync_article_display_content(db, article, seed)
        _sync_article_source(db, seed["id"], seed)
        _insert_article_links(db, seed["id"], seed)
        print(f"  insert demo article: {seed['display_title']}")

    db.commit()
