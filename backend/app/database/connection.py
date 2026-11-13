from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..config import get_settings

_url = get_settings().database_url
_args = {"check_same_thread": False} if _url.startswith("sqlite") else {}
engine = create_engine(_url, connect_args=_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from .models import Base

    Base.metadata.create_all(bind=engine)
