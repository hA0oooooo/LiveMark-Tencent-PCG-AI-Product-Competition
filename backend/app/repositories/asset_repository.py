from sqlalchemy.orm import Session, selectinload

from app.models import Asset


def create(db: Session, data: dict) -> Asset:
    asset = Asset(**data)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def get(db: Session, asset_id: int) -> Asset | None:
    return db.query(Asset).filter(Asset.id == asset_id).first()


def get_detail(db: Session, asset_id: int) -> Asset | None:
    return (
        db.query(Asset)
        .options(selectinload(Asset.frames), selectinload(Asset.clips), selectinload(Asset.publish_plans))
        .filter(Asset.id == asset_id)
        .first()
    )


def list_assets(db: Session, account_id: int | None = None, status: str | None = None) -> list[Asset]:
    query = db.query(Asset)
    if account_id is not None:
        query = query.filter(Asset.account_id == account_id)
    if status:
        query = query.filter(Asset.status == status)
    return query.order_by(Asset.created_at.desc()).all()


def update(db: Session, asset: Asset, data: dict) -> Asset:
    for key, value in data.items():
        setattr(asset, key, value)
    db.commit()
    db.refresh(asset)
    return asset


def delete(db: Session, asset: Asset) -> None:
    db.delete(asset)
    db.commit()
