"""スクレイパーのセーフティーガード。

DDoS・アクセス過多を防ぐためのレートリミッター、robots.txt チェックを提供する。
"""

import time
from threading import Lock
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from batch.settings import settings

_USER_AGENT = "Kuni-Musubi-Bot/1.0"


class DomainRateLimiter:
    """ドメインごとの最終アクセス時刻を管理し、指定間隔を保証するクラス。"""

    def __init__(self, interval_seconds: float):
        self._last_access: dict[str, float] = {}
        self._lock = Lock()
        self.interval_seconds = interval_seconds

    def wait_if_needed(self, url: str) -> None:
        """必要であれば待機してから返る。

        1. URL のドメインを取得する
        2. 前回アクセスからの経過時間を計算する
        3. 不足分をスリープする
        4. アクセス時刻を更新する
        """
        domain = urlparse(url).netloc
        with self._lock:
            last = self._last_access.get(domain, 0.0)
            elapsed = time.monotonic() - last
            wait = self.interval_seconds - elapsed
            if wait > 0:
                time.sleep(wait)
            self._last_access[domain] = time.monotonic()


# バッチ全体で共有するシングルトンインスタンス
domain_rate_limiter = DomainRateLimiter(settings.scraper_domain_interval_seconds)


def check_robots_txt(url: str, user_agent: str = _USER_AGENT) -> bool:
    """robots.txt を取得してアクセス可否を返す。

    取得失敗時は安全側に倒してアクセス許可（True）を返す。

    1. robots.txt の URL を組み立てる
    2. RobotFileParser で取得・パースする
    3. 対象 URL のアクセス可否を返す
    """
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception:
        # robots.txt が存在しないか取得できない場合はアクセス許可とみなす
        return True
    return bool(rp.can_fetch(user_agent, url))


def compute_backoff_seconds(attempt: int, base: float = 1.0, factor: float = 2.0) -> float:
    """指数バックオフの待機秒数を計算する。

    attempt=0 → base 秒、attempt=1 → base*factor 秒、...
    """
    return base * (factor**attempt)
