from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import HistoricalPostBulkCreate, HistoricalPostCreate, HistoricalPostRead, HistoricalPostStatsRead
from app.services import analytics_service, historical_post_service

router = APIRouter(prefix="/api/accounts/{account_id}/historical-posts", tags=["historical_posts"])


@router.post("", response_model=HistoricalPostRead)
def create_post(account_id: int, payload: HistoricalPostCreate, db: Session = Depends(get_db)):
    return historical_post_service.create_post(db, account_id, payload)


@router.post("/bulk", response_model=list[HistoricalPostRead])
def bulk_create_posts(account_id: int, payload: HistoricalPostBulkCreate, db: Session = Depends(get_db)):
    return historical_post_service.bulk_create_posts(db, account_id, payload)


@router.get("", response_model=list[HistoricalPostRead])
def list_posts(account_id: int, db: Session = Depends(get_db)):
    return historical_post_service.list_posts_by_account(db, account_id)


@router.get("/stats", response_model=HistoricalPostStatsRead)
def get_stats(account_id: int, db: Session = Depends(get_db)):
    return analytics_service.get_historical_post_stats(db, account_id)


@router.delete("/{post_id}")
def delete_post(account_id: int, post_id: int, db: Session = Depends(get_db)):
    return historical_post_service.delete_post(db, account_id, post_id)
