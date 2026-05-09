"""LLM 処理ステップ。

フェッチ済み記事テキストを Gemini API に送り、ArticleLLMOutput を返す。
"""

import json
import re
import time

from google import genai
from google.genai import types
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from batch.llm.prompts.article import SYSTEM_PROMPT, build_user_prompt
from batch.llm.schemas.article import ArticleLLMOutput
from batch.settings import settings
from batch.steps.fetch import FetchResult

# 無料枠の厳格なレート制限（20 RPM 等）を確実に回避するためのリクエスト間隔
_RATE_LIMIT_SLEEP = 15


def _is_retryable(exc: BaseException) -> bool:
    """ValueError（設定ミス）はリトライせず、それ以外はリトライ対象とする。"""
    return not isinstance(exc, ValueError)


@retry(
    retry=retry_if_exception(_is_retryable),
    wait=wait_exponential(multiplier=1, min=4, max=30),
    stop=stop_after_attempt(4),
    reraise=True,
)
def _call_gemini(user_prompt: str) -> str:
    """Gemini API を呼び出してテキスト応答を返す。

    429/503 などのサーバーエラーは Exponential Backoff で最大 3 回リトライする。

    1. レートリミット回避のため待機する
    2. Gemini クライアントを初期化する
    3. JSON 出力を強制してコンテンツを生成する
    4. テキスト応答を返す
    """
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY が設定されていません")

    # 1. 無料枠レートリミットを確実に回避するため待機する
    time.sleep(_RATE_LIMIT_SLEEP)

    client = genai.Client(api_key=settings.gemini_api_key)
    response = client.models.generate_content(
        model=settings.llm_model,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=2048,
            temperature=0.2,
            tools=[types.Tool(google_search=types.GoogleSearch())],
        ),
    )
    return response.text or ""


def _extract_json(raw_text: str) -> str:
    """LLM 応答からコードブロックを除去して JSON 文字列を返す。"""
    text = raw_text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()
    return text


def process_article_with_llm(fetch_result: FetchResult) -> ArticleLLMOutput | None:
    """記事テキストを LLM で処理し、検証済みの ArticleLLMOutput を返す。

    エラー時はクラッシュせず None を返す。

    1. ユーザープロンプトを組み立てる
    2. Gemini API を呼び出す（リトライ付き）
    3. コードブロックを除去して JSON をパースする
    4. Pydantic で検証して ArticleLLMOutput を返す
    """
    user_prompt = build_user_prompt(
        article_text=fetch_result.body_text,
        source_url=fetch_result.source_url,
        source_name=fetch_result.source_name,
        published_at=fetch_result.published_at,
    )

    # 2. Gemini API 呼び出し（リトライ上限到達時は None を返す）
    try:
        raw_text = _call_gemini(user_prompt)
    except Exception as exc:
        print(f"[llm] API 呼び出し失敗（リトライ上限）: {exc}")
        return None

    # 3. コードブロック除去 → JSON パース
    json_text = _extract_json(raw_text)
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as exc:
        print(f"[llm] JSON パースエラー: {exc} — raw: {json_text[:200]}")
        return None

    # 4. Pydantic 検証
    try:
        return ArticleLLMOutput.model_validate(data)
    except ValueError as exc:
        print(f"[llm] スキーマ検証エラー: {exc}")
        return None
