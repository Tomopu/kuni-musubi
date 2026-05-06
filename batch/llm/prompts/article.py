"""記事処理用 LLM プロンプト。

docs/technical/20260501_LLM出力スキーマ設計.md の方針に基づく。
プロンプト本文は system_prompt.txt / user_prompt.txt で管理する。
"""

from pathlib import Path

_PROMPTS_DIR = Path(__file__).parent

SYSTEM_PROMPT: str = (_PROMPTS_DIR / "system_prompt.txt").read_text(encoding="utf-8")
USER_PROMPT_TEMPLATE: str = (_PROMPTS_DIR / "user_prompt.txt").read_text(encoding="utf-8")


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
