import json
import shutil
from pathlib import Path

from sqlalchemy import text

from app.config import settings
from app.database import SessionLocal, init_db
from app.repositories import account_repository


SEED_DIR = Path(__file__).resolve().parent / "data" / "seed"


def load_first_account_json() -> dict:
    return json.loads((SEED_DIR / "first_account.json").read_text(encoding="utf-8"))


def seed_first_account(db):
    data = load_first_account_json()
    data = {
        "avg_views": 0,
        "avg_likes": 0,
        "avg_saves": 0,
        "avg_comments": 0,
        "avg_follows": 0,
        **data,
    }
    existing = account_repository.get_default(db)
    if existing:
        return account_repository.update(db, existing, data)
    return account_repository.create(db, data)


def seed_historical_posts(db, account_id: int):
    db.execute(text("DELETE FROM historical_posts"))
    db.commit()
    return []


def clear_demo_runtime_data(db):
    for table in ["post_results", "publish_plans", "clips", "frames", "assets"]:
        db.execute(text(f"DELETE FROM {table}"))
    db.commit()


def clear_runtime_files():
    for directory in [settings.UPLOAD_DIR, settings.FRAME_DIR, settings.CLIP_DIR]:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        for child in path.iterdir():
            if child.name == ".gitkeep":
                continue
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()


def run_seed():
    init_db()
    db = SessionLocal()
    try:
        account = seed_first_account(db)
        seed_historical_posts(db, account.id)
        clear_demo_runtime_data(db)
        clear_runtime_files()
        print(f"Seed completed: account_id={account.id}, historical_posts=0, runtime_assets=0")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
