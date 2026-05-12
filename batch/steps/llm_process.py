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
from batch.llm.schemas.article import ArticleLLMOutput, RelatedParty
from batch.settings import settings
from batch.steps.fetch import FetchResult

# 無料枠の厳格なレート制限（20 RPM 等）を確実に回避するためのリクエスト間隔
_RATE_LIMIT_SLEEP = 15
_VALID_SOURCE_TYPES = {
    "party_official",
    "government",
    "local_government",
    "news_media",
    "other",
}

_PARTY_SHORT_NAMES: dict[str, str] = {
    "自由民主党": "自民",
    "立憲民主党": "立憲",
    "国民民主党": "国民民主",
    "公明党": "公明",
    "日本維新の会": "維新",
    "参政党": "参政",
    "日本共産党": "共産",
    "れいわ新選組": "れいわ",
    "日本保守党": "保守",
    "社会民主党": "社民",
    "チームみらい": "みらい",
    "中道改革連合": "中道改革",
    "減税日本・ゆうこく連合": "減税・ゆうこく",
}

_PARTY_ALIASES: dict[str, str] = {
    **{name: name for name in _PARTY_SHORT_NAMES},
    **{short_name: name for name, short_name in _PARTY_SHORT_NAMES.items()},
}


def _is_retryable(exc: BaseException) -> bool:
    """ValueError（設定ミス）はリトライせず、それ以外はリトライ対象とする。"""
    return not isinstance(exc, ValueError)


@retry(
    retry=retry_if_exception(_is_retryable),
    wait=wait_exponential(multiplier=1, min=4, max=30),
    stop=stop_after_attempt(4),
    reraise=True,
)
def _call_gemini(user_prompt: str, *, use_tools: bool = True) -> str:
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
    config_kwargs: dict[str, object] = {
        "system_instruction": SYSTEM_PROMPT,
        "max_output_tokens": 8192,
        "temperature": 0.2,
    }
    if use_tools:
        config_kwargs["tools"] = [types.Tool(google_search=types.GoogleSearch())]
    else:
        config_kwargs["response_mime_type"] = "application/json"

    response = client.models.generate_content(
        model=settings.llm_model,
        contents=user_prompt,
        config=types.GenerateContentConfig(**config_kwargs),
    )
    return response.text or ""


def _extract_json(raw_text: str) -> str:
    """LLM 応答からコードブロックを除去して JSON 文字列を返す。"""
    text = raw_text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()
    return text


def _parse_json_with_repair(json_text: str) -> dict[str, object] | None:
    """JSON をパースし、失敗時は LLM に JSON 修復だけを依頼する。"""
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as exc:
        print(f"[llm] JSON パースエラー: {exc} — raw: {json_text[:200]}")
    else:
        if isinstance(data, dict):
            return data
        print("[llm] JSON パースエラー: ルート要素が object ではありません")
        return None

    repair_prompt = (
        "次のテキストは壊れた JSON です。意味を変えず、必ず有効な JSON object に修復してください。"
        "説明文、コードブロック、Markdown は出力せず、JSON 文字列のみを返してください。\n\n"
        f"{json_text}"
    )
    try:
        repaired_text = _call_gemini(repair_prompt, use_tools=False)
    except Exception as exc:
        print(f"[llm] JSON 修復失敗（API 呼び出し）: {exc}")
        return None

    repaired_json_text = _extract_json(repaired_text)
    repaired_json_text = (
        repaired_json_text.replace("```json", "").replace("```", "").strip()
    )
    try:
        repaired_data = json.loads(repaired_json_text)
    except json.JSONDecodeError as exc:
        print(f"[llm] JSON 修復後もパース失敗: {exc} — raw: {repaired_json_text[:200]}")
        return None

    if not isinstance(repaired_data, dict):
        print("[llm] JSON 修復後パースエラー: ルート要素が object ではありません")
        return None
    print("[llm] JSON 修復成功")
    return repaired_data


def _normalize_related_parties(
    output: ArticleLLMOutput,
    source_name: str,
) -> ArticleLLMOutput:
    """人物名などを除外し、出典政党を primary として補完する。"""
    normalized: list[RelatedParty] = []
    seen: set[str] = set()

    for related in output.related_parties:
        party_name = _PARTY_ALIASES.get(related.party_name.strip())
        if not party_name or party_name in seen:
            continue
        seen.add(party_name)
        normalized.append(
            RelatedParty(
                party_name=party_name,
                party_short_name=_PARTY_SHORT_NAMES[party_name],
                relation_type=related.relation_type,
            )
        )

    source_party_name = _PARTY_ALIASES.get(source_name.strip())
    if source_party_name and source_party_name not in seen:
        normalized.insert(
            0,
            RelatedParty(
                party_name=source_party_name,
                party_short_name=_PARTY_SHORT_NAMES[source_party_name],
                relation_type="primary",
            ),
        )
    elif source_party_name:
        normalized = [
            RelatedParty(
                party_name=related.party_name,
                party_short_name=related.party_short_name,
                relation_type="primary"
                if related.party_name == source_party_name
                else related.relation_type,
            )
            for related in normalized
        ]

    return output.model_copy(update={"related_parties": normalized})


def _as_list(value: object) -> list[object]:
    """LLM が文字列で返したリスト項目を list に寄せる。"""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        parts = [
            part.strip(" ・-　")
            for part in re.split(r"\n+|[;；]", stripped)
            if part.strip(" ・-　")
        ]
        return parts or [stripped]
    return [value]


def _coerce_llm_data(
    data: dict[str, object],
    fetch_result: FetchResult,
) -> dict[str, object]:
    """LLM 出力の軽微な型ズレ・欠落を Pydantic 検証前に補正する。"""
    coerced = dict(data)

    coerced["remaining_issues"] = [
        str(item) for item in _as_list(coerced.get("remaining_issues"))
    ]

    if isinstance(coerced.get("categories"), str):
        coerced["categories"] = [
            item.strip()
            for item in re.split(r"[,、\n]+", str(coerced["categories"]))
            if item.strip()
        ]
    elif not isinstance(coerced.get("categories"), list):
        coerced["categories"] = []

    if not isinstance(coerced.get("related_parties"), list):
        coerced["related_parties"] = []

    if not isinstance(coerced.get("grounding_sources"), list):
        coerced["grounding_sources"] = []

    public_reactions = coerced.get("public_reactions_summary")
    if isinstance(public_reactions, dict):
        coerced["public_reactions_summary"] = "\n".join(
            f"・{value}" for value in public_reactions.values() if value
        )
    elif public_reactions is None:
        coerced["public_reactions_summary"] = ""
    else:
        coerced["public_reactions_summary"] = str(public_reactions)

    source_summary = coerced.get("source_summary")
    if not isinstance(source_summary, dict):
        source_summary = {}
    else:
        source_summary = dict(source_summary)

    source_type = source_summary.get("source_type") or fetch_result.source_type
    if source_type not in _VALID_SOURCE_TYPES:
        source_type = "other"

    source_summary.setdefault("primary_source_url", fetch_result.source_url)
    source_summary.setdefault("source_name", fetch_result.source_name)
    source_summary.setdefault("published_at", fetch_result.published_at)
    source_summary["source_type"] = source_type
    coerced["source_summary"] = source_summary

    quality_flags = coerced.get("quality_flags")
    if not isinstance(quality_flags, dict):
        quality_flags = {}
    else:
        quality_flags = dict(quality_flags)
    quality_flags.setdefault("is_positive_news", True)
    quality_flags.setdefault("is_solution_oriented", True)
    quality_flags.setdefault("needs_human_review", False)
    quality_flags["risk_notes"] = [
        str(item) for item in _as_list(quality_flags.get("risk_notes"))
    ]
    coerced["quality_flags"] = quality_flags

    return coerced


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
        media_type=fetch_result.media_type,
    )

    # 2. Gemini API 呼び出し（リトライ上限到達時は None を返す）
    try:
        raw_text = _call_gemini(user_prompt)
    except Exception as exc:
        print(f"[llm] API 呼び出し失敗（リトライ上限）: {exc}")
        return None

    # 3. コードブロック除去 → JSON パース
    json_text = _extract_json(raw_text)
    json_text = json_text.replace("```json", "").replace("```", "").strip()
    data = _parse_json_with_repair(json_text)
    if data is None:
        return None
    data = _coerce_llm_data(data, fetch_result)

    # 4. Pydantic 検証
    try:
        output = ArticleLLMOutput.model_validate(data)
    except ValueError as exc:
        print(f"[llm] スキーマ検証エラー: {exc}")
        return None
    return _normalize_related_parties(output, fetch_result.source_name)
