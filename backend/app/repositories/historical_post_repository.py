from sqlalchemy.orm import Session

from app.models import HistoricalPost


def create(db: Session, data: dict) -> HistoricalPost:
    post = HistoricalPost(**data)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def get(db: Session, post_id: int) -> HistoricalPost | None:
    return db.query(HistoricalPost).filter(HistoricalPost.id == post_id).first()


def update(db: Session, post: HistoricalPost, data: dict) -> HistoricalPost:
    for key, value in data.items():
        setattr(post, key, value)
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


def delete(db: Session, post: HistoricalPost) -> None:
    db.delete(post)
    db.commit()
