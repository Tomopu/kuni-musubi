# シードデータ投入スクリプト
# 既存データがある場合はスキップする（冪等実行可能）

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.db.models import Party, PolicyCategory
from app.infrastructure.db.seeds.demo_articles import seed_demo_articles
from app.infrastructure.db.seeds.parties import PARTY_SEEDS
from app.infrastructure.db.seeds.policy_categories import POLICY_CATEGORY_SEEDS
from app.infrastructure.db.session import SessionLocal


def seed_parties(db: Session) -> None:
    # 1. 各政党を ID または政党名で検索し、JSON の内容に同期する
    for data in PARTY_SEEDS:
        existing = db.get(Party, data["id"])
        if existing is None:
            existing = db.scalars(
                select(Party).where(Party.name == data["name"])
            ).first()
        if existing is not None:
            for key, value in data.items():
                setattr(existing, key, value)
            print(f"  update party: {data['name']}")
            continue
        party = Party(**data)
        db.add(party)
        print(f"  insert party: {data['name']}")
    db.commit()


def seed_policy_categories(db: Session) -> None:
    # 1. 各カテゴリを ID で検索し、存在しない場合のみ INSERT する
    for data in POLICY_CATEGORY_SEEDS:
        existing = db.get(PolicyCategory, data["id"])
        if existing is not None:
            for key, value in data.items():
                setattr(existing, key, value)
            print(f"  update category: {data['name']}")
            continue
        category = PolicyCategory(**data)
        db.add(category)
        print(f"  insert category: {data['name']}")
    db.commit()


def run() -> None:
    db = SessionLocal()
    try:
        print("Seeding parties...")
        seed_parties(db)
        print("Seeding policy categories...")
        seed_policy_categories(db)
        print("Seeding demo articles...")
        seed_demo_articles(db)
        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
