"""政党管理の JSON エクスポート機能のテスト。"""

import json
import uuid
from datetime import datetime, timezone
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
            "official_url": "https://example.com",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }
    ]


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
