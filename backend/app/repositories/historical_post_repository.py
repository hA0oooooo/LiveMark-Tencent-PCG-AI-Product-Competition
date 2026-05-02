from sqlalchemy.orm import Session

from app.models import HistoricalPost


def create(db: Session, data: dict) -> HistoricalPost:
    post = HistoricalPost(**data)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def bulk_create(db: Session, rows: list[dict]) -> list[HistoricalPost]:
    posts = [HistoricalPost(**row) for row in rows]
    db.add_all(posts)
    db.commit()
    for post in posts:
        db.refresh(post)
    return posts


def list_by_account(db: Session, account_id: int) -> list[HistoricalPost]:
    return (
        db.query(HistoricalPost)
        .filter(HistoricalPost.account_id == account_id)
        .order_by(HistoricalPost.publish_time.desc().nullslast(), HistoricalPost.id.desc())
        .all()
    )


def delete_by_account(db: Session, account_id: int) -> None:
    db.query(HistoricalPost).filter(HistoricalPost.account_id == account_id).delete()
    db.commit()
