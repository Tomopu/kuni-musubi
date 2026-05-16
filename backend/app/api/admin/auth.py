"""管理者認証ユーティリティ。"""

import uuid
from typing import Optional

import bcrypt
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy.orm import Session

from app.infrastructure.db.models import AdminUser
from app.settings import Settings

settings = Settings()
_serializer = URLSafeTimedSerializer(settings.admin_secret_key)

COOKIE_NAME = "admin_session"
SESSION_MAX_AGE = 86400 * 7  # 7日間


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_session_token(user_id: uuid.UUID) -> str:
    return _serializer.dumps(str(user_id))


def verify_session_token(token: str) -> Optional[str]:
    try:
        return _serializer.loads(token, max_age=SESSION_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None


def authenticate_admin(db: Session, username: str, password: str) -> Optional[AdminUser]:
    # 1. ユーザー名でレコードを取得する
    user = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not user:
        return None
    # 2. パスワードを検証する
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_current_admin(request: object, db: Session) -> Optional[AdminUser]:
    # 1. クッキーからトークンを取得する
    token = getattr(request, "cookies", {}).get(COOKIE_NAME)
    if not token:
        return None
    # 2. トークンを検証して user_id を取得する
    user_id = verify_session_token(token)
    if not user_id:
        return None
    # 3. DB からユーザーを取得する
    return db.query(AdminUser).filter(AdminUser.id == user_id).first()
