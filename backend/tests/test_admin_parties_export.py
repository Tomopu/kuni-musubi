"""政党管理の JSON エクスポート機能のテスト。"""

import json
import uuid
from datetime import date, datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


def test_write_parties_export(tmp_path) -> None:
    """parties の現在値を JSON ファイルとして保存できる。"""
    from app.api.admin.router import _write_parties_export

    party_id = uuid.UUID("11111111-0000-0000-0000-000000000001")
    now = datetime(2026, 5, 13, 12, 0, tzinfo=timezone.utc)
    party = SimpleNamespace(
        id=party_id,
        name="自由民主党",
        short_name="自民",
        color_hex="#009933",
        is_active=True,
        display_order=1,
        founded_year=1955,
        leader_name="テスト代表",
        house_of_representatives_seats=196,
        house_of_councillors_seats=100,
        ideology_summary="保守政党",
        manifesto_summary="経済成長",
        manifesto_promises=["経済成長", "安全保障"],
        main_policy_categories=["経済", "外交"],
        policy_headline="日本列島を、強く豊かに。",
        policy_headline_type="政策スローガン",
        policy_pillars=["強い経済", "地方創生"],
        main_policy_tags=["経済成長", "地方創生"],
        policy_source_type="公式政策パンフレット",
        policy_source_label="自由民主党「公約・政策パンフレット」",
        policy_source_url="https://example.com/policy",
        policy_last_checked=date(2026, 5, 13),
        policy_note="確認済み",
        official_url="https://example.com",
        created_at=now,
        updated_at=now,
    )

    export_path = tmp_path / "parties_export.json"
    result_path = _write_parties_export([party], export_path)

    assert result_path == export_path
    payload = json.loads(export_path.read_text(encoding="utf-8"))
    assert payload == [
        {
            "id": str(party_id),
            "name": "自由民主党",
            "short_name": "自民",
            "color_hex": "#009933",
            "is_active": True,
            "display_order": 1,
            "founded_year": 1955,
            "leader_name": "テスト代表",
            "house_of_representatives_seats": 196,
            "house_of_councillors_seats": 100,
            "ideology_summary": "保守政党",
            "manifesto_summary": "経済成長",
            "manifesto_promises": ["経済成長", "安全保障"],
            "main_policy_categories": ["経済", "外交"],
            "policy_headline": "日本列島を、強く豊かに。",
            "policy_headline_type": "政策スローガン",
            "policy_pillars": ["強い経済", "地方創生"],
            "main_policy_tags": ["経済成長", "地方創生"],
            "policy_source_type": "公式政策パンフレット",
            "policy_source_label": "自由民主党「公約・政策パンフレット」",
            "policy_source_url": "https://example.com/policy",
            "policy_last_checked": "2026-05-13",
            "policy_note": "確認済み",
            "official_url": "https://example.com",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }
    ]


def test_normalize_text_list_accepts_postgres_array_literal() -> None:
    """文字列化された PostgreSQL 配列を項目単位に戻せる。"""
    from app.usecases.party_field_utils import normalize_text_list

    assert normalize_text_list(
        "{社会保険料を下げて暮らしを変える,副首都から起動する経済成長,教育・保育の無償化と質の向上}"
    ) == [
        "社会保険料を下げて暮らしを変える",
        "副首都から起動する経済成長",
        "教育・保育の無償化と質の向上",
    ]


def test_normalize_text_list_removes_char_level_newlines_in_array_literal() -> None:
    """配列リテラル内で1文字ごとに入った改行を取り除ける。"""
    from app.usecases.party_field_utils import normalize_text_list

    assert normalize_text_list(
        "{\n強\nい\n経\n済\nで\n、\n笑\n顔\nあ\nふ\nれ\nる\n暮\nら\nし\nを\n。\n,\n地\n方\nが\n日\n本\n経\n済\nの\nエ\nン\nジ\nン\nに\n。\n}"
    ) == [
        "強い経済で、笑顔あふれる暮らしを。",
        "地方が日本経済のエンジンに。",
    ]


def test_normalize_text_list_repairs_char_array_literal_items() -> None:
    """DBに文字単位の TEXT[] として保存された値を項目配列に戻せる。"""
    from app.usecases.party_field_utils import normalize_text_list

    assert normalize_text_list(
        ["{", "強", "い", "経", "済", ",", "地", "方", "創", "生", "}"]
    ) == ["強い経済", "地方創生"]


def test_write_parties_export_normalizes_array_literal_strings(tmp_path) -> None:
    """JSON保存時に配列リテラル文字列を文字単位に分解しない。"""
    from app.api.admin.router import _write_parties_export

    party = SimpleNamespace(
        id=uuid.UUID("11111111-0000-0000-0000-000000000001"),
        name="テスト党",
        short_name="テスト",
        color_hex="#009933",
        is_active=True,
        display_order=1,
        founded_year=None,
        leader_name=None,
        house_of_representatives_seats=None,
        house_of_councillors_seats=None,
        ideology_summary=None,
        manifesto_summary=None,
        manifesto_promises="{強い経済,地方創生}",
        main_policy_categories="{経済,地方}",
        policy_headline=None,
        policy_headline_type=None,
        policy_pillars=["{", "強", "い", "経", "済", ",", "地", "方", "創", "生", "}"],
        main_policy_tags=["{", "経", "済", "成", "長", ",", "地", "方", "創", "生", "}"],
        policy_source_type=None,
        policy_source_label=None,
        policy_source_url=None,
        policy_last_checked=None,
        policy_note=None,
        official_url=None,
        created_at=None,
        updated_at=None,
    )

    export_path = tmp_path / "parties_export.json"
    _write_parties_export([party], export_path)
    payload = json.loads(export_path.read_text(encoding="utf-8"))

    assert payload[0]["policy_pillars"] == ["強い経済", "地方創生"]
    assert payload[0]["main_policy_tags"] == ["経済成長", "地方創生"]


def test_parties_export_json_route(client: TestClient, tmp_path) -> None:
    """管理画面の JSON 保存ボタン用ルートがファイル保存してリダイレクトする。"""
    from app.infrastructure.db.session import get_db
    from app.main import app

    mock_party = SimpleNamespace(
        id=uuid.UUID("11111111-0000-0000-0000-000000000001"),
        name="自由民主党",
        short_name="自民",
        color_hex="#009933",
        is_active=True,
        display_order=1,
        founded_year=None,
        leader_name=None,
        house_of_representatives_seats=None,
        house_of_councillors_seats=None,
        ideology_summary=None,
        manifesto_summary=None,
        manifesto_promises=[],
        main_policy_categories=[],
        policy_headline=None,
        policy_headline_type=None,
        policy_pillars=[],
        main_policy_tags=[],
        policy_source_type=None,
        policy_source_label=None,
        policy_source_url=None,
        policy_last_checked=None,
        policy_note=None,
        official_url=None,
        created_at=None,
        updated_at=None,
    )
    mock_session = MagicMock()
    mock_session.query.return_value.order_by.return_value.all.return_value = [mock_party]

    def _mock_db():
        yield mock_session

    app.dependency_overrides[get_db] = _mock_db
    try:
        with (
            patch("app.api.admin.router.get_current_admin", return_value=MagicMock()),
            patch("app.api.admin.router.PARTIES_EXPORT_PATH", tmp_path / "parties.json"),
        ):
            resp = client.post("/admin/parties/export-json", follow_redirects=False)
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert resp.status_code == 302
    assert "/admin/parties" in resp.headers["location"]
    assert (tmp_path / "parties.json").exists()


def test_party_form_accepts_string_policy_last_checked(client: TestClient) -> None:
    """DBドライバ差異で policy_last_checked が文字列でも編集画面を描画できる。"""
    from app.infrastructure.db.session import get_db
    from app.main import app

    party_id = uuid.UUID("11111111-0000-0000-0000-000000000001")
    mock_party = SimpleNamespace(
        id=party_id,
        name="自由民主党",
        short_name="自民",
        color_hex="#009933",
        is_active=True,
        display_order=1,
        founded_year=1955,
        leader_name="テスト代表",
        house_of_representatives_seats=196,
        house_of_councillors_seats=100,
        official_url="https://example.com",
        policy_headline="日本列島を、強く豊かに。",
        policy_headline_type="政策スローガン",
        policy_source_type="公式政策パンフレット",
        policy_source_label="自由民主党「公約・政策パンフレット」",
        policy_pillars="{\n強\nい\n経\n済\n,\n地\n方\n創\n生\n}",
        main_policy_tags="{経済成長,地方創生}",
        policy_source_url="https://example.com/policy",
        policy_last_checked="2026-05-13",
        policy_note=None,
        ideology_summary=None,
        manifesto_summary=None,
        manifesto_promises=[],
        main_policy_categories=[],
    )
    mock_session = MagicMock()
    mock_session.query.return_value.filter.return_value.first.return_value = mock_party

    def _mock_db():
        yield mock_session

    app.dependency_overrides[get_db] = _mock_db
    try:
        with patch("app.api.admin.router.get_current_admin", return_value=MagicMock()):
            resp = client.get(f"/admin/parties/{party_id}/edit")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert resp.status_code == 200
    assert 'value="2026-05-13"' in resp.text
    assert "強\nい\n経\n済" not in resp.text
    assert "経\n済\n成\n長" not in resp.text
    assert "強い経済\n地方創生" in resp.text
    assert "経済成長\n地方創生" in resp.text
