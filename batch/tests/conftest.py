"""batch テスト共通設定。

LLM スキーマテストは DB 不要のため PYTHONPATH 設定は不要。
save.py など backend モデルを使うテストは PYTHONPATH=../backend が必要。
"""

from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def block_http_requests():
    """テスト中に実際の HTTP リクエストが発生しないことを保証する安全装置。

    個別テストで _fetch_single_url 等を patch している場合は、
    このフィクスチャは透過的に動作する（httpx.Client.send が呼ばれないため）。
    万が一 patch 漏れがあった場合にネットワーク到達前でエラーを発生させる。
    """
    with patch("httpx.Client.send") as mock_send:
        mock_send.side_effect = RuntimeError(
            "テスト中に実際の HTTP リクエストが発行されました。"
            " 対象の関数を patch してください。"
        )
        yield mock_send
