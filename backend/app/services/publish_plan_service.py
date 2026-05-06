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
    title = clean_user_text(data.get("recommended_title") or data.get("title") or fallback["recommended_title"])
    cover_text = clean_user_text(data.get("cover_text", ""))
    caption = clean_user_text(data.get("caption", ""))
    comment_prompt = clean_user_text(data.get("comment_prompt", ""))
    recommended_publish_time = clean_user_text(data.get("recommended_publish_time", ""))
    ai_strategy = clean_user_text(data.get("ai_strategy", ""))
    hashtags = data.get("hashtags", [])
    if isinstance(hashtags, list):
        hashtags = [clean_user_text(str(item)) for item in hashtags]
        hashtags_value = json.dumps(hashtags, ensure_ascii=False)
    else:
        hashtags_value = clean_user_text(str(hashtags))
    return publish_plan_repository.create(
        db,
        {
            "clip_id": clip.id,
            "asset_id": asset.id,
            "account_id": account.id,
            "title": title,
            "cover_text": cover_text,
            "caption": caption,
            "hashtags": hashtags_value,
            "comment_prompt": comment_prompt,
            "recommended_publish_time": recommended_publish_time,
            "target_metric": normalize_target_metric(data.get("target_metric"), clip.target_metric),
            "status": "draft",
            "ai_strategy": ai_strategy,
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
    for key in ["title", "cover_text", "caption", "hashtags", "comment_prompt", "recommended_publish_time", "ai_strategy"]:
        if key in data and isinstance(data[key], str):
            data[key] = clean_user_text(data[key])
    updated = publish_plan_repository.update(db, plan, data)
    if updated.status == "reviewed":
        asset = asset_repository.get(db, updated.asset_id)
        if asset:
            asset_repository.update(db, asset, {"status": "reviewed"})
    return updated


def clean_user_text(text: str) -> str:
    replacements = {
        "target_metric": "目标指标",
        "Target Metric": "目标指标",
        "Metric": "指标",
        "Click": "点击",
        "click": "点击",
        "Save": "收藏",
        "save": "收藏",
        "Comment": "评论",
        "comment": "评论",
        "Follow": "关注",
        "follow": "关注",
        "Long Tail": "长尾回看",
        "long_tail": "长尾现场型",
        "interaction": "互动型",
        "high_quality_collection": "高清收藏型",
        "persona_detail": "人设细节型",
        "emotion": "情绪氛围型",
        "timely": "抢鲜型",
        "compilation": "合集型",
    }
    cleaned = text or ""
    for source, target in replacements.items():
        cleaned = cleaned.replace(source, target)
    return cleaned


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
