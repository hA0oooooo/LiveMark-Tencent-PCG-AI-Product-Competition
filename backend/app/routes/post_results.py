from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import PostResultCreate, PostResultRead
from app.services import review_service

router = APIRouter(tags=["post_results"])


@router.post("/api/post-results", response_model=PostResultRead)
def create_post_result(payload: PostResultCreate, db: Session = Depends(get_db)):
    return review_service.create_post_result_and_review(db, payload)


@router.get("/api/post-results/{post_result_id}", response_model=PostResultRead)
def get_post_result(post_result_id: int, db: Session = Depends(get_db)):
    return review_service.get_post_result(db, post_result_id)


@router.get("/api/publish-plans/{plan_id}/post-result", response_model=PostResultRead)
def get_post_result_by_plan(plan_id: int, db: Session = Depends(get_db)):
    return review_service.get_post_result_by_plan(db, plan_id)
