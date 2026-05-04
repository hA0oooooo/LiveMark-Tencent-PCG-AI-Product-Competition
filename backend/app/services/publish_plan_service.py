import json
from sqlalchemy.orm import Session

from app.models import HistoricalPost, PostResult
from app.exceptions import not_found
from app.repositories import asset_repository, publish_plan_repository
from app.services import account_service, analytics_service, clip_service, memory_service, modelscope_service, xhs_strategy_service
from app.schemas import PublishPlanUpdate

ALLOWED_TARGET_METRICS = {"click", "save", "comment", "follow", "long_tail"}


def normalize_target_metric(value: str | None, fallback: str) -> str:
    return value if value in ALLOWED_TARGET_METRICS else fallback


def build_default_publish_schedule(clips: list) -> list:
    priority = [
        lambda clip: clip.clip_type == "interaction" or clip.rarity_score >= 70,
        lambda clip: clip.clip_type in {"emotion", "high_quality_collection"},
        lambda clip: clip.clip_type in {"long_tail", "persona_detail"},
    ]
    selected = []
    remaining = list(clips)
    for rule in priority:
        match = next((clip for clip in remaining if rule(clip)), None)
        if match:
            selected.append(match)
            remaining.remove(match)
    for clip in remaining:
        if len(selected) >= 3:
            break
        selected.append(clip)
    return selected[:3]


def generate_plan_for_clip(db: Session, clip_id: int):
    clip = clip_service.get_clip(db, clip_id)
    asset = asset_repository.get(db, clip.asset_id)
    if not asset:
        raise not_found("未找到素材")
    account = account_service.get_account(db, asset.account_id)
    benchmark = analytics_service.get_account_benchmark(db, account.id)
    memory_context = memory_service.build_publish_context(db, account, asset, clip, benchmark)
    llm_plan = modelscope_service.generate_publish_plan_with_llm(account, asset, clip, benchmark, memory_context)
    fallback = xhs_strategy_service.build_fallback_plan(asset, clip)
    data = {**fallback, **{k: v for k, v in llm_plan.items() if v}}
    return publish_plan_repository.create(
        db,
        {
            "clip_id": clip.id,
            "asset_id": asset.id,
            "account_id": account.id,
            "title": data.get("recommended_title") or data.get("title") or fallback["recommended_title"],
            "cover_text": data.get("cover_text", ""),
            "caption": data.get("caption", ""),
            "hashtags": json.dumps(data.get("hashtags", []), ensure_ascii=False)
            if isinstance(data.get("hashtags"), list)
            else str(data.get("hashtags", "")),
            "comment_prompt": data.get("comment_prompt", ""),
            "recommended_publish_time": data.get("recommended_publish_time", ""),
            "target_metric": normalize_target_metric(data.get("target_metric"), clip.target_metric),
            "status": "draft",
            "ai_strategy": data.get("ai_strategy", ""),
        },
    )


def generate_publish_matrix_for_asset(db: Session, asset_id: int):
    asset = asset_repository.get(db, asset_id)
    if not asset:
        raise not_found("未找到素材")
    account_service.get_account(db, asset.account_id)
    clips = clip_service.list_clips_by_asset(db, asset_id)
    if not clips:
        raise not_found("该素材还没有候选片段，请先完成 AI 分析")
    scheduled = build_default_publish_schedule(clips)
    plans = [generate_plan_for_clip(db, clip.id) for clip in scheduled]
    asset_repository.update(db, asset, {"status": "plan_generated"})
    return plans


def list_plans(db: Session, account_id: int | None = None, asset_id: int | None = None, status: str | None = None):
    return publish_plan_repository.list_plans(db, account_id, asset_id, status)


def get_plan(db: Session, plan_id: int):
    plan = publish_plan_repository.get(db, plan_id)
    if not plan:
        raise not_found("未找到发布计划")
    return plan


def update_plan(db: Session, plan_id: int, update_data: PublishPlanUpdate):
    plan = get_plan(db, plan_id)
    data = update_data.model_dump(exclude_unset=True)
    if isinstance(data.get("hashtags"), list):
        data["hashtags"] = json.dumps(data["hashtags"], ensure_ascii=False)
    updated = publish_plan_repository.update(db, plan, data)
    if updated.status == "reviewed":
        asset = asset_repository.get(db, updated.asset_id)
        if asset:
            asset_repository.update(db, asset, {"status": "reviewed"})
    return updated


def delete_plan(db: Session, plan_id: int):
    plan = get_plan(db, plan_id)
    account_id = plan.account_id
    result = db.query(PostResult).filter(PostResult.publish_plan_id == plan.id).first()
    if result:
        if result.historical_post_id:
            db.query(HistoricalPost).filter(HistoricalPost.id == result.historical_post_id).delete()
        db.delete(result)
        db.commit()
    publish_plan_repository.delete(db, plan)
    account_service.recalculate_account_baseline(db, account_id)
    return {"message": "发布计划已删除"}
