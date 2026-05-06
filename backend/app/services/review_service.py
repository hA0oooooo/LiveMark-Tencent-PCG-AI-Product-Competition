import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.exceptions import not_found
from app.repositories import (
    account_repository,
    asset_repository,
    historical_post_repository,
    post_result_repository,
    publish_plan_repository,
)
from app.schemas import PostResultCreate
from app.services import analytics_service, memory_service, modelscope_service
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


def generate_review_text(db: Session, account, plan, result, benchmark) -> tuple[str, str, str]:
    memory_context = memory_service.build_review_context(db, account, plan, result, benchmark)
    review = modelscope_service.generate_post_review_with_llm(account, plan, result, benchmark, memory_context)
    memory_suggestion = review.get("memory_update_suggestion", {})
    return json.dumps(review, ensure_ascii=False), review.get("next_action", ""), json.dumps(memory_suggestion, ensure_ascii=False)


def create_post_result_and_review(db: Session, result_create: PostResultCreate):
    plan = publish_plan_repository.get(db, result_create.publish_plan_id)
    if not plan:
        raise not_found("未找到发布计划")
    account = account_repository.get(db, plan.account_id)
    if not account:
        raise not_found("未找到账户")
    benchmark = analytics_service.get_account_benchmark(db, account.id)
    metrics = compute_post_metrics(result_create)
    lifts = compute_relative_lifts(result_create, benchmark)
    data = {**result_create.model_dump(), **metrics, **lifts, "ai_review": "", "next_action": ""}
    existing = post_result_repository.get_by_plan(db, result_create.publish_plan_id)
    result = post_result_repository.update(db, existing, data) if existing else post_result_repository.create(db, data)
    ai_review, next_action, ai_memory_suggestion = generate_review_text(db, account, plan, result, benchmark)
    result.ai_review = ai_review
    result.next_action = next_action
    result.ai_memory_suggestion = ai_memory_suggestion
    db.commit()
    db.refresh(result)
    sync_review_to_historical_post(db, account, plan, result)
    publish_plan_repository.update(db, plan, {"status": "reviewed"})
    asset = asset_repository.get(db, plan.asset_id)
    if asset:
        asset_repository.update(db, asset, {"status": "reviewed"})
    return result


def sync_review_to_historical_post(db: Session, account, plan, result):
    clip_type = getattr(getattr(plan, "clip", None), "clip_type", None) or "long_tail"
    data = {
        "account_id": account.id,
        "title": result.actual_title or plan.title,
        "content_type": clip_type,
        "publish_time": result.actual_publish_time or datetime.utcnow(),
        "views": result.views,
        "likes": result.likes,
        "saves": result.saves,
        "comments": result.comments,
        "shares": 0,
        "follows": result.follows,
        "has_interaction": clip_type == "interaction",
        "has_emotion": clip_type == "emotion",
        "has_rare_view": clip_type in {"timely", "long_tail", "persona_detail"},
        "has_cover_text": bool(plan.cover_text),
        "has_bgm": False,
        "creator_note": f"由发布计划 #{plan.id} 的内容实验复盘同步生成",
    }
    post = historical_post_repository.get(db, result.historical_post_id) if result.historical_post_id else None
    if post:
        historical_post_repository.update(db, post, data)
    else:
        post = historical_post_repository.create(db, data)
        result.historical_post_id = post.id
        db.commit()
        db.refresh(result)
    from app.services import account_service

    account_service.recalculate_account_baseline(db, account.id)


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


def integrate_memory_from_post_result(db: Session, post_result_id: int):
    result = get_post_result(db, post_result_id)
    plan = publish_plan_repository.get(db, result.publish_plan_id)
    if not plan:
        raise not_found("未找到发布计划")
    account = account_repository.get(db, plan.account_id)
    if not account:
        raise not_found("未找到账户")
    try:
        suggestion = json.loads(result.ai_memory_suggestion or "{}")
    except json.JSONDecodeError:
        suggestion = {}
    current_memory = {
        "strategy_summary": account.strategy_summary or "",
        "shooting_style_memory": account.shooting_style_memory or "",
        "content_direction_memory": account.content_direction_memory or "",
        "audience_preference_memory": account.audience_preference_memory or "",
        "negative_lessons": account.negative_lessons or "",
    }
    integrated = modelscope_service.integrate_account_memory_with_llm(current_memory, suggestion)
    integrated["updated_memory_at"] = datetime.utcnow()
    return account_repository.update(db, account, integrated)
