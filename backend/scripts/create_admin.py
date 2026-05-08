#!/usr/bin/env python
"""管理者アカウント作成スクリプト。

使い方（backend/ ディレクトリから）:
    uv run python scripts/create_admin.py --username admin --password yourpassword
"""

import argparse
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))

from app.infrastructure.db.models import AdminUser, Base
from app.infrastructure.db.session import SessionLocal, engine
from app.api.admin.auth import hash_password


def main() -> None:
    parser = argparse.ArgumentParser(description="管理者アカウントを作成する")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing = db.query(AdminUser).filter(AdminUser.username == args.username).first()
        if existing:
            print(f"[create_admin] ユーザー '{args.username}' は既に存在します。パスワードを更新します。")
            existing.hashed_password = hash_password(args.password)
        else:
            user = AdminUser(
                username=args.username,
                hashed_password=hash_password(args.password),
            )
            db.add(user)
            print(f"[create_admin] ユーザー '{args.username}' を作成しました。")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
