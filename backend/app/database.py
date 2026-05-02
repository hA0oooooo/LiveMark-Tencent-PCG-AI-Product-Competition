from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings


connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


SQLITE_SCHEMA_COLUMNS = {
    "accounts": {
        "current_note_count": "INTEGER DEFAULT 0",
        "total_likes": "INTEGER DEFAULT 0",
        "total_saves": "INTEGER DEFAULT 0",
        "strategy_summary": "TEXT DEFAULT ''",
        "shooting_style_memory": "TEXT DEFAULT ''",
        "content_direction_memory": "TEXT DEFAULT ''",
        "audience_preference_memory": "TEXT DEFAULT ''",
        "negative_lessons": "TEXT DEFAULT ''",
        "updated_memory_at": "DATETIME",
    },
    "assets": {
        "context_note": "TEXT DEFAULT ''",
    },
    "historical_posts": {
        "shares": "INTEGER DEFAULT 0",
    },
    "clips": {
        "editing_advice": "TEXT DEFAULT ''",
        "account_fit_reason": "TEXT DEFAULT ''",
    },
    "post_results": {
        "ai_memory_suggestion": "TEXT DEFAULT ''",
    },
}


def ensure_sqlite_schema_columns() -> None:
    if not settings.DATABASE_URL.startswith("sqlite"):
        return
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    with engine.begin() as connection:
        for table, columns in SQLITE_SCHEMA_COLUMNS.items():
            if table not in existing_tables:
                continue
            existing_columns = {column["name"] for column in inspector.get_columns(table)}
            for column_name, column_type in columns.items():
                if column_name not in existing_columns:
                    connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column_name} {column_type}"))


def init_db() -> None:
    from app import models  # noqa: F401
    from app.utils.file_utils import ensure_dir

    ensure_dir(settings.DATA_DIR)
    ensure_dir(settings.UPLOAD_DIR)
    ensure_dir(settings.FRAME_DIR)
    ensure_dir(settings.CLIP_DIR)
    Base.metadata.create_all(bind=engine)
    ensure_sqlite_schema_columns()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
