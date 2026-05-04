# 日本の政党シードデータ
# docs/research/data/20260504_government_data.json を正として読み込む。

import json
import uuid
from pathlib import Path
from typing import Any


RESEARCH_DATA_FILENAME = "20260504_government_data.json"


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


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def load_party_seeds() -> list[dict[str, Any]]:
    with RESEARCH_DATA_PATH.open(encoding="utf-8") as f:
        raw_parties = json.load(f)

    seeds: list[dict[str, Any]] = []
    for index, item in enumerate(raw_parties, start=1):
        name = str(item["政党名"]).strip()
        manifesto_promises = _string_list(item.get("主要政策・公約"))
        seeds.append(
            {
                "id": PARTY_IDS_BY_NAME[name],
                "name": name,
                "short_name": _string_or_none(item.get("略称")) or name,
                "color_hex": _string_or_none(item.get("テーマカラー")),
                "is_active": True,
                "display_order": index,
                "founded_year": _int_or_none(item.get("成立年")),
                "leader_name": _string_or_none(item.get("代表者")),
                "house_of_representatives_seats": _int_or_none(
                    item.get("衆議院議席数")
                ),
                "house_of_councillors_seats": _int_or_none(
                    item.get("参議院議席数")
                ),
                "ideology_summary": _string_or_none(item.get("党の政治理念")),
                "manifesto_summary": "\n".join(manifesto_promises) or None,
                "manifesto_promises": manifesto_promises,
                "main_policy_categories": _string_list(item.get("主な政策カテゴリ")),
                "official_url": _string_or_none(item.get("公式サイトURL")),
            }
        )
    return seeds


PARTY_SEEDS = load_party_seeds()
