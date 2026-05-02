from datetime import datetime

from sqlalchemy.orm import Session

from app.exceptions import not_found
from app.repositories import account_repository, historical_post_repository
from app.schemas import AccountCreate, AccountUpdate


def create_account(db: Session, account_create: AccountCreate):
    data = account_create.model_dump()
    data["platform"] = "小红书"
    return account_repository.create(db, data)


def get_account(db: Session, account_id: int):
    account = account_repository.get(db, account_id)
    if not account:
        raise not_found("未找到账号")
    return account


def list_accounts(db: Session):
    return account_repository.list_all(db)


def update_account(db: Session, account_id: int, account_update: AccountUpdate):
    account = get_account(db, account_id)
    data = account_update.model_dump(exclude_unset=True)
    data.pop("platform", None)
    memory_fields = {
        "strategy_summary",
        "shooting_style_memory",
        "content_direction_memory",
        "audience_preference_memory",
        "negative_lessons",
    }
    if memory_fields.intersection(data):
        data["updated_memory_at"] = datetime.utcnow()
    return account_repository.update(db, account, data)


def get_default_account(db: Session):
    account = account_repository.get_default(db)
    if not account:
        raise not_found("未找到默认账号，请先运行 seed")
    return account


def recalculate_account_baseline(db: Session, account_id: int):
    account = get_account(db, account_id)
    posts = historical_post_repository.list_by_account(db, account_id)
    count = len(posts)
    if count == 0:
        return account_repository.update(
            db,
            account,
            {"avg_views": 0, "avg_likes": 0, "avg_saves": 0, "avg_comments": 0, "avg_follows": 0},
        )
    follows_values = [post.follows or 0 for post in posts]
    avg_follows = sum(follows_values) / count if any(follows_values) else 0
    return account_repository.update(
        db,
        account,
        {
            "avg_views": sum(post.views for post in posts) / count,
            "avg_likes": sum(post.likes for post in posts) / count,
            "avg_saves": sum(post.saves for post in posts) / count,
            "avg_comments": sum(post.comments for post in posts) / count,
            "avg_follows": avg_follows,
        },
    )
