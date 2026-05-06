"""LLM 処理ステップ。

フェッチ済み記事テキストを Gemini API に送り、ArticleLLMOutput を返す。
"""

import json

from google import genai
from google.genai import types

from batch.llm.prompts.article import SYSTEM_PROMPT, build_user_prompt
from batch.llm.schemas.article import ArticleLLMOutput
from batch.settings import settings
from batch.steps.fetch import FetchResult


def _call_gemini(user_prompt: str) -> str:
    """Gemini API を呼び出してテキスト応答を返す。

    1. Gemini クライアントを初期化する
    2. システム指示とユーザープロンプトでコンテンツを生成する
    3. テキスト応答を返す
    """
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY が設定されていません")

    client = genai.Client(api_key=settings.gemini_api_key)
    response = client.models.generate_content(
        model=settings.llm_model,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=2048,
            temperature=0.2,
        ),
    )
    return response.text or ""


def process_article_with_llm(fetch_result: FetchResult) -> ArticleLLMOutput:
    """記事テキストを LLM で処理し、検証済みの ArticleLLMOutput を返す。

    1. ユーザープロンプトを組み立てる
    2. Gemini API を呼び出す
    3. JSON をパースして Pydantic で検証する
    4. ArticleLLMOutput を返す
    """
    user_prompt = build_user_prompt(
        article_text=fetch_result.body_text,
        source_url=fetch_result.source_url,
        source_name=fetch_result.source_name,
        published_at=fetch_result.published_at,
    )

    raw_text = _call_gemini(user_prompt)

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
