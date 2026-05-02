import json
from sqlalchemy.orm import Session

from app.exceptions import not_found
from app.repositories import account_repository, asset_repository, post_result_repository, publish_plan_repository
from app.schemas import PostResultCreate
from app.services import analytics_service, modelscope_service
from app.utils.metric_utils import compute_lift, compute_rate


def compute_post_metrics(result_create: PostResultCreate) -> dict:
    return {
        "like_rate": compute_rate(result_create.likes, result_create.views),
        "save_rate": compute_rate(result_create.saves, result_create.views),
        "comment_rate": compute_rate(result_create.comments, result_create.views),
        "follow_rate": compute_rate(result_create.follows or 0, result_create.views),
    }


def compute_relative_lifts(metrics_source, benchmark: dict) -> dict:
    return {
        "relative_view_lift": compute_lift(metrics_source.views, benchmark.get("avg_views")),
        "relative_like_lift": compute_lift(metrics_source.likes, benchmark.get("avg_likes")),
        "relative_save_lift": compute_lift(metrics_source.saves, benchmark.get("avg_saves")),
        "relative_comment_lift": compute_lift(metrics_source.comments, benchmark.get("avg_comments")),
        "relative_follow_lift": compute_lift(metrics_source.follows or 0, benchmark.get("avg_follows")),
    }


def generate_review_text(account, plan, result, benchmark) -> tuple[str, str]:
    review = modelscope_service.generate_post_review_with_llm(account, plan, result, benchmark)
    return json.dumps(review, ensure_ascii=False), review.get("next_action", "")


def create_post_result_and_review(db: Session, result_create: PostResultCreate):
    plan = publish_plan_repository.get(db, result_create.publish_plan_id)
    if not plan:
        raise not_found("未找到发布计划")
    account = account_repository.get(db, plan.account_id)
    if not account:
        raise not_found("未找到账号")
    benchmark = analytics_service.get_account_benchmark(db, account.id)
    metrics = compute_post_metrics(result_create)
    lifts = compute_relative_lifts(result_create, benchmark)
    data = {**result_create.model_dump(), **metrics, **lifts, "ai_review": "", "next_action": ""}
    result = post_result_repository.create(db, data)
    ai_review, next_action = generate_review_text(account, plan, result, benchmark)
    result.ai_review = ai_review
    result.next_action = next_action
    db.commit()
    db.refresh(result)
    publish_plan_repository.update(db, plan, {"status": "reviewed"})
    asset = asset_repository.get(db, plan.asset_id)
    if asset:
        asset_repository.update(db, asset, {"status": "reviewed"})
    return result


def get_post_result(db: Session, post_result_id: int):
    result = post_result_repository.get(db, post_result_id)
    if not result:
        raise not_found("未找到复盘结果")
    return result


def get_post_result_by_plan(db: Session, plan_id: int):
    result = post_result_repository.get_by_plan(db, plan_id)
    if not result:
        raise not_found("该发布计划还没有复盘结果")
    return result
