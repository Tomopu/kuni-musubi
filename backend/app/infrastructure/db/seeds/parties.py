# 日本の政党シードデータ
# docs/research/data/parties_export.json を正として読み込む。

import json
import uuid
from datetime import date
from pathlib import Path
from typing import Any


RESEARCH_DATA_FILENAME = "parties_export.json"


def _resolve_research_data_path() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        candidate = parent / "docs" / "research" / "data" / RESEARCH_DATA_FILENAME
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"Could not find docs/research/data/{RESEARCH_DATA_FILENAME}"
    )


RESEARCH_DATA_PATH = _resolve_research_data_path()

PARTY_IDS_BY_NAME = {
    "自由民主党": uuid.UUID("11111111-0000-0000-0000-000000000001"),
    "立憲民主党": uuid.UUID("11111111-0000-0000-0000-000000000002"),
    "日本維新の会": uuid.UUID("11111111-0000-0000-0000-000000000003"),
    "国民民主党": uuid.UUID("11111111-0000-0000-0000-000000000004"),
    "参政党": uuid.UUID("11111111-0000-0000-0000-000000000005"),
    "日本共産党": uuid.UUID("11111111-0000-0000-0000-000000000006"),
    "れいわ新選組": uuid.UUID("11111111-0000-0000-0000-000000000007"),
    "社会民主党": uuid.UUID("11111111-0000-0000-0000-000000000008"),
    "チームみらい": uuid.UUID("11111111-0000-0000-0000-000000000009"),
    "公明党": uuid.UUID("11111111-0000-0000-0000-000000000010"),
    "中道改革連合": uuid.UUID("11111111-0000-0000-0000-000000000011"),
    "日本保守党": uuid.UUID("11111111-0000-0000-0000-000000000012"),
    "減税日本・ゆうこく連合": uuid.UUID("11111111-0000-0000-0000-000000000013"),
    "無所属": uuid.UUID("11111111-0000-0000-0000-000000000014"),
}


def _string_or_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _int_or_none(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _date_or_none(value: Any) -> date | None:
    if value is None or value == "":
        return None
    return date.fromisoformat(str(value))


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def load_party_seeds() -> list[dict[str, Any]]:
    with RESEARCH_DATA_PATH.open(encoding="utf-8") as f:
        raw_parties = json.load(f)

    seeds: list[dict[str, Any]] = []
    for index, item in enumerate(raw_parties, start=1):
        name = str(item["name"]).strip()
        policy_pillars = _string_list(item.get("policy_pillars"))
        main_policy_tags = _string_list(item.get("main_policy_tags"))
        seeds.append(
            {
                "id": uuid.UUID(item["id"]) if item.get("id") else PARTY_IDS_BY_NAME[name],
                "name": name,
                "short_name": _string_or_none(item.get("short_name")) or name,
                "color_hex": _string_or_none(item.get("color_hex")),
                "is_active": bool(item.get("is_active", True)),
                "display_order": _int_or_none(item.get("display_order")) or index,
                "founded_year": _int_or_none(item.get("founded_year")),
                "leader_name": _string_or_none(item.get("leader_name")),
                "house_of_representatives_seats": _int_or_none(
                    item.get("house_of_representatives_seats")
                ),
                "house_of_councillors_seats": _int_or_none(
                    item.get("house_of_councillors_seats")
                ),
                "policy_headline": _string_or_none(item.get("policy_headline")),
                "policy_headline_type": _string_or_none(item.get("policy_headline_type")),
                "policy_pillars": policy_pillars,
                "main_policy_tags": main_policy_tags,
                "policy_source_type": _string_or_none(item.get("policy_source_type")),
                "policy_source_label": _string_or_none(item.get("policy_source_label")),
                "policy_source_url": _string_or_none(item.get("policy_source_url")),
                "policy_last_checked": _date_or_none(item.get("policy_last_checked")),
                "policy_note": _string_or_none(item.get("policy_note")),
                "official_url": _string_or_none(item.get("official_url")),
                # 旧 API / 画面との互換用。export に値があれば尊重し、なければ新データから導出する。
                "ideology_summary": _string_or_none(
                    item.get("ideology_summary")
                ) or _string_or_none(item.get("policy_headline")),
                "manifesto_summary": _string_or_none(
                    item.get("manifesto_summary")
                ) or ("\n".join(policy_pillars) or None),
                "manifesto_promises": _string_list(
                    item.get("manifesto_promises")
                ) or policy_pillars,
                "main_policy_categories": _string_list(
                    item.get("main_policy_categories")
                ) or main_policy_tags,
            }
        )
    return seeds


PARTY_SEEDS = load_party_seeds()
