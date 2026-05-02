import json
from pathlib import Path

from app.database import SessionLocal, init_db
from app.repositories import account_repository, historical_post_repository
from app.services import account_service, historical_post_service


SEED_DIR = Path(__file__).resolve().parent / "data" / "seed"


def load_first_account_json() -> dict:
    return json.loads((SEED_DIR / "first_account.json").read_text(encoding="utf-8"))


def load_historical_posts_csv():
    return historical_post_service.load_posts_from_csv(SEED_DIR / "historical_posts.csv")


def seed_first_account(db):
    data = load_first_account_json()
    existing = account_repository.get_by_name(db, data["name"])
    if existing:
        return account_repository.update(db, existing, data)
    return account_repository.create(db, data)


def seed_historical_posts(db, account_id: int):
    historical_post_repository.delete_by_account(db, account_id)
    posts = load_historical_posts_csv()
    return historical_post_service.bulk_create_posts(db, account_id, posts)


def recalculate_seed_account_baseline(db, account_id: int):
    return account_service.recalculate_account_baseline(db, account_id)


def run_seed():
    init_db()
    db = SessionLocal()
    try:
        account = seed_first_account(db)
        seed_historical_posts(db, account.id)
        recalculate_seed_account_baseline(db, account.id)
        print(f"Seed completed: account_id={account.id}")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
