from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ClipRead
from app.services import clip_service

router = APIRouter(tags=["clips"])


@router.get("/api/assets/{asset_id}/clips", response_model=list[ClipRead])
def list_clips_by_asset(asset_id: int, db: Session = Depends(get_db)):
    return clip_service.list_clips_by_asset(db, asset_id)


@router.get("/api/clips/{clip_id}", response_model=ClipRead)
def get_clip(clip_id: int, db: Session = Depends(get_db)):
    return clip_service.get_clip(db, clip_id)
