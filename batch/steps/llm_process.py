"""LLM 処理ステップ。

フェッチ済み記事テキストを Anthropic API に送り、ArticleLLMOutput を返す。
"""

import json

import httpx

from batch.llm.prompts.article import SYSTEM_PROMPT, build_user_prompt
from batch.llm.schemas.article import ArticleLLMOutput
from batch.settings import settings
from batch.steps.fetch import FetchResult

_ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
_ANTHROPIC_VERSION = "2023-06-01"


def _call_anthropic(user_prompt: str) -> str:
    """Anthropic Messages API を呼び出してテキスト応答を返す。

    1. リクエストボディを組み立てる
    2. POST リクエストを送信する
    3. content[0].text を返す
    """
    if not settings.anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY が設定されていません")

    payload = {
        "model": settings.llm_model,
        "max_tokens": 2048,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_prompt}],
    }
    headers = {
        "x-api-key": settings.anthropic_api_key,
        "anthropic-version": _ANTHROPIC_VERSION,
        "content-type": "application/json",
    }

    with httpx.Client(timeout=60) as client:
        resp = client.post(_ANTHROPIC_API_URL, json=payload, headers=headers)
        resp.raise_for_status()

    data = resp.json()
    return str(data["content"][0]["text"])


def process_article_with_llm(fetch_result: FetchResult) -> ArticleLLMOutput:
    """記事テキストを LLM で処理し、検証済みの ArticleLLMOutput を返す。

    1. ユーザープロンプトを組み立てる
    2. Anthropic API を呼び出す
    3. JSON をパースして Pydantic で検証する
    4. ArticleLLMOutput を返す
    """
    user_prompt = build_user_prompt(
        article_text=fetch_result.body_text,
        source_url=fetch_result.source_url,
        source_name=fetch_result.source_name,
        published_at=fetch_result.published_at,
    )

    raw_text = _call_anthropic(user_prompt)

    # LLM がコードブロックで囲む場合があるので除去する
    # 例: ```json\n{...}\n``` → {...}
    raw_text = raw_text.strip()
    if raw_text.startswith("```"):
        lines = raw_text.split("\n")
        # 1行目（```json など言語識別子行）と末尾の``` を除去する
        inner_lines = lines[1:]
        if inner_lines and inner_lines[-1].strip().startswith("```"):
            inner_lines = inner_lines[:-1]
        raw_text = "\n".join(inner_lines).strip()

    data = json.loads(raw_text)
    return ArticleLLMOutput.model_validate(data)
