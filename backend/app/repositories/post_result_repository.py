from sqlalchemy.orm import Session

from app.models import PostResult


def create(db: Session, data: dict) -> PostResult:
    result = PostResult(**data)
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def get(db: Session, post_result_id: int) -> PostResult | None:
    return db.query(PostResult).filter(PostResult.id == post_result_id).first()


def get_by_plan(db: Session, plan_id: int) -> PostResult | None:
    return db.query(PostResult).filter(PostResult.publish_plan_id == plan_id).first()


def list_all(db: Session) -> list[PostResult]:
    return db.query(PostResult).order_by(PostResult.created_at.desc()).all()
