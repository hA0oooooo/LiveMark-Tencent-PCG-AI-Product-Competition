from sqlalchemy.orm import Session

from app.models import PublishPlan


def create(db: Session, data: dict) -> PublishPlan:
    plan = PublishPlan(**data)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def bulk_create(db: Session, rows: list[dict]) -> list[PublishPlan]:
    plans = [PublishPlan(**row) for row in rows]
    db.add_all(plans)
    db.commit()
    for plan in plans:
        db.refresh(plan)
    return plans


def list_plans(
    db: Session,
    account_id: int | None = None,
    asset_id: int | None = None,
    status: str | None = None,
) -> list[PublishPlan]:
    query = db.query(PublishPlan)
    if account_id is not None:
        query = query.filter(PublishPlan.account_id == account_id)
    if asset_id is not None:
        query = query.filter(PublishPlan.asset_id == asset_id)
    if status:
        query = query.filter(PublishPlan.status == status)
    return query.order_by(PublishPlan.created_at.desc()).all()


def get(db: Session, plan_id: int) -> PublishPlan | None:
    return db.query(PublishPlan).filter(PublishPlan.id == plan_id).first()


def update(db: Session, plan: PublishPlan, data: dict) -> PublishPlan:
    for key, value in data.items():
        if value is not None:
            setattr(plan, key, value)
    db.commit()
    db.refresh(plan)
    return plan
