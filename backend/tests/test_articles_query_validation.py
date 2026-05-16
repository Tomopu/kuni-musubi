"""GET /articles のクエリパラメータバリデーションテスト。

DB 操作が必要なため、正常系は DB なしでは深くテストできない。
ここでは 422 になるべき不正入力のみを確認する。
"""

from fastapi.testclient import TestClient


class TestGetArticlesQueryValidation:
    """GET /articles のクエリパラメータバリデーション。"""

    def test_invalid_sort_value(self, client: TestClient) -> None:
        """sort に invalid な値は 422 を返す。"""
        resp = client.get("/articles?sort=invalid")
        assert resp.status_code == 422

    def test_limit_too_large(self, client: TestClient) -> None:
        """limit が 50 超は 422 を返す。"""
        resp = client.get("/articles?limit=51")
        assert resp.status_code == 422

    def test_limit_zero(self, client: TestClient) -> None:
        """limit が 0 は 422 を返す。"""
        resp = client.get("/articles?limit=0")
        assert resp.status_code == 422

    def test_invalid_party_id_format(self, client: TestClient) -> None:
        """UUID でない party_id は 422 を返す。"""
        resp = client.get("/articles?party_id=not-a-uuid")
        assert resp.status_code == 422

    def test_valid_sort_latest(self, client: TestClient) -> None:
        """sort=latest は 422 ではない（DB なし時は 200 または 500）。"""
        resp = client.get("/articles?sort=latest")
        assert resp.status_code != 422

    def test_valid_sort_important(self, client: TestClient) -> None:
        """sort=important は 422 ではない（DB なし時は 200 または 500）。"""
        resp = client.get("/articles?sort=important")
        assert resp.status_code != 422

    def test_valid_limit_boundary(self, client: TestClient) -> None:
        """limit=50 は 422 ではない。"""
        resp = client.get("/articles?limit=50")
        assert resp.status_code != 422
