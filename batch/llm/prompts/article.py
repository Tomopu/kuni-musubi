"""記事処理用 LLM プロンプト。

docs/technical/20260501_LLM出力スキーマ設計.md の方針に基づく。
プロンプト本文は system_prompt.txt / user_prompt.txt で管理する。
"""

from pathlib import Path

_PROMPTS_DIR = Path(__file__).parent

SYSTEM_PROMPT: str = (_PROMPTS_DIR / "system_prompt.txt").read_text(encoding="utf-8")
USER_PROMPT_TEMPLATE: str = (_PROMPTS_DIR / "user_prompt.txt").read_text(encoding="utf-8")

# メディア種別ごとに追加する処理指示
_MEDIA_TYPE_INSTRUCTIONS: dict[str, str] = {
    "pdf": (
        "これは公文書（PDF）のテキストです。"
        "お役所言葉を避け、結論から先に、中学生でもわかるように解説してください。"
    ),
    "youtube": (
        "これは国会審議等の書き起こしです。"
        "冗長な挨拶などを省き、生活者に直結する重要な発言を抜き出して要約してください。"
    ),
}


def build_user_prompt(
    article_text: str,
    source_url: str,
    source_name: str,
    published_at: str,
    media_type: str = "html",
) -> str:
    """記事テキストとメタ情報からユーザープロンプトを生成する。"""
    # メディア種別に応じた処理指示を先頭に付加する
    instruction = _MEDIA_TYPE_INSTRUCTIONS.get(media_type, "")
    prefix = f"[追加指示] {instruction}\n\n" if instruction else ""
    return USER_PROMPT_TEMPLATE.format(
        article_text=prefix + article_text[:8000],
        source_url=source_url,
        source_name=source_name,
        published_at=published_at,
    )
