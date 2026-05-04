from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from batch.settings import settings

_engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)


def get_session() -> Generator[Session, None, None]:
    """DB セッションを生成してクローズするジェネレータ。"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
