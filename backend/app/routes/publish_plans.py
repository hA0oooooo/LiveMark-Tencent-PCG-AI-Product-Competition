from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import PublishPlanRead, PublishPlanUpdate
from app.services import publish_plan_service

router = APIRouter(tags=["publish_plans"])


@router.post("/api/assets/{asset_id}/generate-publish-matrix", response_model=list[PublishPlanRead])
def generate_publish_matrix(asset_id: int, db: Session = Depends(get_db)):
    return publish_plan_service.generate_publish_matrix_for_asset(db, asset_id)


@router.get("/api/publish-plans", response_model=list[PublishPlanRead])
def list_plans(
    account_id: int | None = None,
    asset_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return publish_plan_service.list_plans(db, account_id, asset_id, status)


@router.get("/api/publish-plans/{plan_id}", response_model=PublishPlanRead)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    return publish_plan_service.get_plan(db, plan_id)


@router.put("/api/publish-plans/{plan_id}", response_model=PublishPlanRead)
def update_plan(plan_id: int, payload: PublishPlanUpdate, db: Session = Depends(get_db)):
    return publish_plan_service.update_plan(db, plan_id, payload)


@router.delete("/api/publish-plans/{plan_id}")
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    return publish_plan_service.delete_plan(db, plan_id)
