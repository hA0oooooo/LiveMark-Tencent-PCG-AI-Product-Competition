from sqlalchemy.orm import Session

from app.models import Clip


def create(db: Session, data: dict) -> Clip:
    clip = Clip(**data)
    db.add(clip)
    db.commit()
    db.refresh(clip)
    return clip


def bulk_create(db: Session, rows: list[dict]) -> list[Clip]:
    clips = [Clip(**row) for row in rows]
    db.add_all(clips)
    db.commit()
    for clip in clips:
        db.refresh(clip)
    return clips


def list_by_asset(db: Session, asset_id: int) -> list[Clip]:
    return db.query(Clip).filter(Clip.asset_id == asset_id).order_by(Clip.growth_score.desc()).all()


def get(db: Session, clip_id: int) -> Clip | None:
    return db.query(Clip).filter(Clip.id == clip_id).first()


def delete_by_asset(db: Session, asset_id: int) -> None:
    db.query(Clip).filter(Clip.asset_id == asset_id).delete()
    db.commit()
