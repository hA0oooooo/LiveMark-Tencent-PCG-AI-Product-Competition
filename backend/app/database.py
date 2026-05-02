from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings


connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    from app import models  # noqa: F401
    from app.utils.file_utils import ensure_dir

    ensure_dir(settings.DATA_DIR)
    ensure_dir(settings.UPLOAD_DIR)
    ensure_dir(settings.FRAME_DIR)
    ensure_dir(settings.CLIP_DIR)
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
