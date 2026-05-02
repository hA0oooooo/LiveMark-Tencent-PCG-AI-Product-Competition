from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AssetAnalysisResponse, AssetDetailRead, AssetRead, AssetUploadResponse
from app.services import asset_service

router = APIRouter(prefix="/api/assets", tags=["assets"])


@router.post("/upload", response_model=AssetUploadResponse)
def upload_asset(
    file: UploadFile = File(...),
    account_id: int = Form(...),
    event_name: str = Form(...),
    scene_type: str = Form(""),
    target_person: str = Form(""),
    context_note: str = Form(""),
    db: Session = Depends(get_db),
):
    asset = asset_service.create_asset_from_upload(db, file, account_id, event_name, scene_type, target_person, context_note)
    return {"asset": asset, "message": "素材上传成功"}


@router.get("", response_model=list[AssetRead])
def list_assets(account_id: int | None = None, status: str | None = None, db: Session = Depends(get_db)):
    return asset_service.list_assets(db, account_id, status)


@router.get("/{asset_id}", response_model=AssetDetailRead)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    return asset_service.get_asset_detail(db, asset_id)


@router.post("/{asset_id}/analyze", response_model=AssetAnalysisResponse)
def analyze_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = asset_service.analyze_asset(db, asset_id)
    return {"asset": asset, "message": "AI 分析完成"}
