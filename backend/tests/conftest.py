"""pytest 共通フィクスチャ。

DB 依存なしでテストできるよう、get_db を MagicMock でオーバーライドする。
"""

import os
from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

os.environ.setdefault("SKIP_DB_INIT", "true")

from app.infrastructure.db.session import get_db
from app.main import app


def _mock_db_session() -> Generator[MagicMock, None, None]:
    """DB セッションをモックに差し替えるジェネレータ。"""
    mock_session = MagicMock(spec=Session)
    # コミットとクローズをノーオプにする
    mock_session.commit.return_value = None
    mock_session.add.return_value = None
    mock_session.close.return_value = None
    yield mock_session


@pytest.fixture
def client() -> TestClient:
    """DB 依存を差し替えた FastAPI TestClient を返す。"""
    app.dependency_overrides[get_db] = _mock_db_session
    c = TestClient(app, raise_server_exceptions=False)
    yield c
    app.dependency_overrides.clear()
