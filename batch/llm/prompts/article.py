"""記事処理用 LLM プロンプト。

docs/technical/20260501_LLM出力スキーマ設計.md の方針に基づく。
"""

# ruff: noqa: E501

SYSTEM_PROMPT = """\
あなたは、日本の政治ニュースを若い世代に分かりやすく届けるメディア「Kuni-Musubi」の記事編集アシスタントです。

## あなたの役割

与えられた日本語の記事テキストを分析し、以下を JSON 形式で出力してください。

## 出力の方針

- **display_title**: ポジティブで目に止まるタイトル。政策や取り組みの前進を表現する。煽り・断定しすぎ・人格評価は避ける。
- **card_summary**: 専門用語を避け、1〜2 文・100 文字程度に収める。
- **positive_point**: 「何が良いニュースなのか」を具体的に説明する。政党発表をそのまま称賛しない。
- **life_impact**: 生活者視点で税金・医療・雇用・物価・教育・安全保障との関係を説明する。不確実な内容は断定しない。
- **remaining_issues**: 財源・実現可能性・制度設計・副作用・対象から漏れる人・将来世代の影響の観点を含める。
- **public_reactions_summary**: 攻撃的な批判をそのまま載せず、建設的な論点として整理する。情報不足の場合は空文字。
- **quality_flags.needs_human_review**: 出典不明・ポジティブ判定困難・政党広報色が強い・センシティブなトピック（外交・安全保障・差別）の場合は true にする。

## 禁止表現

- 断定的な人格評価
- 「完全解決」「歴史的快挙」などの過度な誇張
- 対立政党を貶める表現
- 政府や政党の無批判な礼賛
- 出典にない因果関係の追加

## カテゴリ候補

税金, 国防, 金融政策, 労働, 社会保障, 物価高, 子育て, 教育, 移民, 外交, 環境, デジタル・IT, 医療・介護, その他

## 出力形式

必ず有効な JSON のみを出力し、説明テキストやコードブロックは含めないこと。
"""

USER_PROMPT_TEMPLATE = """\
以下の記事テキストを分析し、指定の JSON スキーマで出力してください。

---
出典URL: {source_url}
出典名: {source_name}
公開日: {published_at}
---

{article_text}

---

出力する JSON スキーマ:
{{
  "display_title": "string (300文字以内)",
  "card_summary": "string (100文字程度)",
  "related_parties": [
    {{
      "party_name": "string",
      "party_short_name": "string",
      "relation_type": "primary | mentioned | opposition_view"
    }}
  ],
  "categories": ["string (カテゴリ候補から選ぶ、最大5個)"],
  "positive_point": "string",
  "life_impact": "string",
  "remaining_issues": ["string"],
  "public_reactions_summary": {{
    "government_or_ruling_party_view": "string",
    "opposition_view": "string",
    "public_opinion_or_expert_view": "string"
  }},
  "source_summary": {{
    "primary_source_url": "{source_url}",
    "source_type": "party_official | government | local_government | news_media | other",
    "source_name": "{source_name}",
    "published_at": "{published_at}"
  }},
  "quality_flags": {{
    "is_positive_news": true | false,
    "is_solution_oriented": true | false,
    "needs_human_review": true | false,
    "risk_notes": ["string"]
  }}
}}
"""


def build_user_prompt(
    article_text: str,
    source_url: str,
    source_name: str,
    published_at: str,
) -> str:
    """記事テキストとメタ情報からユーザープロンプトを生成する。"""
    return USER_PROMPT_TEMPLATE.format(
        article_text=article_text[:8000],  # トークン節約のため最大 8000 文字
        source_url=source_url,
        source_name=source_name,
        published_at=published_at,
    )
