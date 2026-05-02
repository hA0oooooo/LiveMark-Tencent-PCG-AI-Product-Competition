from sqlalchemy.orm import Session

from app.models import Frame


def create(db: Session, data: dict) -> Frame:
    frame = Frame(**data)
    db.add(frame)
    db.commit()
    db.refresh(frame)
    return frame


def bulk_create(db: Session, rows: list[dict]) -> list[Frame]:
    frames = [Frame(**row) for row in rows]
    db.add_all(frames)
    db.commit()
    for frame in frames:
        db.refresh(frame)
    return frames


def list_by_asset(db: Session, asset_id: int) -> list[Frame]:
    return db.query(Frame).filter(Frame.asset_id == asset_id).order_by(Frame.timestamp.asc()).all()


def delete_by_asset(db: Session, asset_id: int) -> None:
    db.query(Frame).filter(Frame.asset_id == asset_id).delete()
    db.commit()


def update(db: Session, frame: Frame, data: dict) -> Frame:
    for key, value in data.items():
        setattr(frame, key, value)
    db.commit()
    db.refresh(frame)
    return frame
