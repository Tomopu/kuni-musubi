"""政党データの表示用フィールドを扱うユーティリティ。"""

import csv
import json
from typing import Any


def normalize_text_list(value: Any) -> list[str]:
    """DBドライバ差異で文字列化された配列値を list[str] に正規化する。"""
    if value is None:
        return []
    if isinstance(value, str):
        return _normalize_text(value)
    if isinstance(value, (list, tuple, set)):
        joined = "".join(str(item) for item in value).strip()
        if _looks_like_array_text(joined):
            return _normalize_text(joined)
        items: list[str] = []
        for item in value:
            if isinstance(item, str) and _looks_like_array_text(item):
                items.extend(_normalize_text(item))
            elif item is not None:
                text = _clean_array_item(str(item))
                if text:
                    items.append(text)
        return items
    text = str(value).strip()
    return [text] if text else []


def text_list_lines(value: Any) -> str:
    """textarea 用に list 相当値を改行区切り文字列へ変換する。"""
    return "\n".join(normalize_text_list(value))


def _normalize_text(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if text.startswith("[") and text.endswith("]"):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, list):
            return normalize_text_list(parsed)
    if text.startswith("{") and text.endswith("}"):
        return _parse_postgres_text_array(text)
    if "\n" in text:
        return [line.strip() for line in text.splitlines() if line.strip()]
    return [text]


def _looks_like_array_text(text: str) -> bool:
    text = text.strip()
    return (text.startswith("{") and text.endswith("}")) or (
        text.startswith("[") and text.endswith("]")
    )


def _parse_postgres_text_array(text: str) -> list[str]:
    inner = text.strip()[1:-1]
    if not inner:
        return []
    inner = inner.replace("\r", "").replace("\n", "")
    reader = csv.reader([inner], quotechar='"', escapechar="\\")
    return [
        cleaned
        for item in next(reader)
        if item != "NULL" and (cleaned := _clean_array_item(item))
    ]


def _clean_array_item(item: str) -> str:
    """配列リテラル内で1文字ごとに入った改行を表示用に取り除く。"""
    item = item.strip()
    if "\n" not in item and "\r" not in item:
        return item
    return "".join(line.strip() for line in item.splitlines() if line.strip())
