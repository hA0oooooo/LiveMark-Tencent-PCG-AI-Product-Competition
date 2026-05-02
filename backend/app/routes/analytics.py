from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ContentTypePerformanceRead, DashboardStatsRead, GrowthInsightsRead
from app.services import analytics_service

router = APIRouter(tags=["analytics"])


@router.get("/api/dashboard/{account_id}", response_model=DashboardStatsRead)
def get_dashboard(account_id: int, db: Session = Depends(get_db)):
    return analytics_service.get_dashboard_stats(db, account_id)


@router.get("/api/accounts/{account_id}/content-type-performance", response_model=list[ContentTypePerformanceRead])
def get_content_type_performance(account_id: int, db: Session = Depends(get_db)):
    return analytics_service.get_content_type_performance(db, account_id)


@router.get("/api/accounts/{account_id}/growth-insights", response_model=GrowthInsightsRead)
def get_growth_insights(account_id: int, db: Session = Depends(get_db)):
    return {"insights": analytics_service.get_growth_insights(db, account_id)}
