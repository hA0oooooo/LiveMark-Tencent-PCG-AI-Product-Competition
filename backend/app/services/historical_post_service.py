import csv
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

from app.exceptions import not_found
from app.models import PostResult
from app.repositories import historical_post_repository
from app.schemas import HistoricalPostBulkCreate, HistoricalPostCreate
from app.services import account_service


def create_post(db: Session, account_id: int, post_create: HistoricalPostCreate):
    account_service.get_account(db, account_id)
    post = historical_post_repository.create(db, {"account_id": account_id, **post_create.model_dump()})
    account_service.recalculate_account_baseline(db, account_id)
    return post


def bulk_create_posts(db: Session, account_id: int, posts: HistoricalPostBulkCreate | list[HistoricalPostCreate]):
    account_service.get_account(db, account_id)
    items = posts.posts if isinstance(posts, HistoricalPostBulkCreate) else posts
    created = historical_post_repository.bulk_create(
        db,
        [{"account_id": account_id, **post.model_dump()} for post in items],
    )
    account_service.recalculate_account_baseline(db, account_id)
    return created


def list_posts_by_account(db: Session, account_id: int):
    account_service.get_account(db, account_id)
    return historical_post_repository.list_by_account(db, account_id)


def delete_post(db: Session, account_id: int, post_id: int):
    account_service.get_account(db, account_id)
    post = historical_post_repository.get(db, post_id)
    if not post or post.account_id != account_id:
        raise not_found("历史内容不存在")
    db.query(PostResult).filter(PostResult.historical_post_id == post_id).update({"historical_post_id": None})
    historical_post_repository.delete(db, post)
    account_service.recalculate_account_baseline(db, account_id)
    return {"message": "历史内容已删除"}


def normalize_historical_post_row(row: dict) -> HistoricalPostCreate:
    def as_bool(value) -> bool:
        return str(value).strip().lower() in {"1", "true", "yes", "y", "是"}

    def as_int(value, default=0):
        if value in (None, ""):
            return default
        return int(float(value))

    publish_time = row.get("publish_time") or None
    parsed_time = datetime.fromisoformat(publish_time) if publish_time else None
    return HistoricalPostCreate(
        title=row.get("title", "未命名历史内容"),
        content_type=row.get("content_type", "long_tail"),
        publish_time=parsed_time,
        views=as_int(row.get("views")),
        likes=as_int(row.get("likes")),
        saves=as_int(row.get("saves")),
        comments=as_int(row.get("comments")),
        shares=as_int(row.get("shares")),
        has_interaction=as_bool(row.get("has_interaction")),
        has_emotion=as_bool(row.get("has_emotion")),
        has_rare_view=as_bool(row.get("has_rare_view")),
        has_cover_text=as_bool(row.get("has_cover_text")),
        has_bgm=as_bool(row.get("has_bgm")),
    )


def load_posts_from_csv(file_path: str | Path) -> list[HistoricalPostCreate]:
    with Path(file_path).open("r", encoding="utf-8-sig", newline="") as f:
        return [normalize_historical_post_row(row) for row in csv.DictReader(f)]
