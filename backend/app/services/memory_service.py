import json
from typing import Any

from sqlalchemy.orm import Session

from app.models import PostResult, PublishPlan
from app.repositories import historical_post_repository
from app.utils.metric_utils import compute_rate


def account_profile_memory(account: Any) -> dict:
    return {
        "name": account.name,
        "platform": account.platform,
        "niche": account.niche,
        "target_audience": account.target_audience,
        "style_positioning": account.style_positioning,
        "follower_count": account.follower_count,
        "strategy_summary": account.strategy_summary,
        "shooting_style_memory": account.shooting_style_memory,
        "content_direction_memory": account.content_direction_memory,
        "audience_preference_memory": account.audience_preference_memory,
        "negative_lessons": account.negative_lessons,
        "updated_memory_at": account.updated_memory_at.isoformat() if account.updated_memory_at else None,
    }


def historical_content_type_stats(db: Session, account_id: int) -> list[dict]:
    posts = historical_post_repository.list_by_account(db, account_id)
    grouped: dict[str, list] = {}
    for post in posts:
        grouped.setdefault(post.content_type, []).append(post)
    rows = []
    for content_type, items in grouped.items():
        count = len(items)
        avg_views = sum(item.views for item in items) / count
        avg_likes = sum(item.likes for item in items) / count
        avg_saves = sum(item.saves for item in items) / count
        avg_comments = sum(item.comments for item in items) / count
        avg_follows = sum((item.follows or 0) for item in items) / count if any((item.follows or 0) for item in items) else 0
        rows.append(
            {
                "content_type": content_type,
                "count": count,
                "avg_views": round(avg_views, 1),
                "avg_like_rate": round(compute_rate(avg_likes, avg_views), 4),
                "avg_save_rate": round(compute_rate(avg_saves, avg_views), 4),
                "avg_comment_rate": round(compute_rate(avg_comments, avg_views), 4),
                "avg_follow_rate": round(compute_rate(avg_follows, avg_views), 4),
            }
        )
    return sorted(rows, key=lambda row: (row["avg_follow_rate"], row["avg_comment_rate"], row["avg_save_rate"]), reverse=True)


def recent_account_learning(db: Session, account_id: int, limit: int = 5) -> list[dict]:
    rows = (
        db.query(PostResult, PublishPlan)
        .join(PublishPlan, PostResult.publish_plan_id == PublishPlan.id)
        .filter(PublishPlan.account_id == account_id)
        .order_by(PostResult.created_at.desc())
        .limit(limit)
        .all()
    )
    learning = []
    for result, plan in rows:
        parsed = {}
        try:
            parsed = json.loads(result.ai_review or "{}")
        except Exception:
            parsed = {}
        learning.append(
            {
                "plan_title": plan.title,
                "target_metric": plan.target_metric,
                "next_action": result.next_action,
                "account_learning": parsed.get("account_learning", ""),
                "memory_suggestion": result.ai_memory_suggestion,
                "relative_view_lift": result.relative_view_lift,
                "relative_follow_lift": result.relative_follow_lift,
            }
        )
    return learning


def build_publish_context(db: Session, account: Any, asset: Any, clip: Any, benchmark: dict) -> dict:
    return {
        "account_profile": account_profile_memory(account),
        "account_benchmark": benchmark,
        "historical_content_type_stats": historical_content_type_stats(db, account.id),
        "recent_account_learning": recent_account_learning(db, account.id),
        "asset_info": {
            "event_name": asset.event_name,
            "scene_type": asset.scene_type,
            "target_person": asset.target_person,
            "context_note": asset.context_note,
            "duration": asset.duration,
            "summary": asset.summary,
        },
        "clip_info": {
            "start_time": clip.start_time,
            "end_time": clip.end_time,
            "clip_type": clip.clip_type,
            "editing_advice": clip.editing_advice,
            "account_fit_reason": clip.account_fit_reason,
        },
        "clip_scores": {
            "growth_score": clip.growth_score,
            "interaction_score": clip.interaction_score,
            "emotion_score": clip.emotion_score,
            "rarity_score": clip.rarity_score,
            "clarity_score": clip.clarity_score,
            "title_cover_score": clip.title_cover_score,
            "account_fit_score": clip.account_fit_score,
        },
    }


def build_review_context(db: Session, account: Any, publish_plan: Any, post_result: Any, benchmark: dict) -> dict:
    return {
        "account_profile": account_profile_memory(account),
        "account_benchmark": benchmark,
        "historical_content_type_stats": historical_content_type_stats(db, account.id),
        "recent_account_learning": recent_account_learning(db, account.id),
        "publish_plan": {
            "title": publish_plan.title,
            "cover_text": publish_plan.cover_text,
            "target_metric": publish_plan.target_metric,
            "ai_strategy": publish_plan.ai_strategy,
        },
        "post_result_metrics": {
            "views": post_result.views,
            "likes": post_result.likes,
            "saves": post_result.saves,
            "comments": post_result.comments,
            "follows": post_result.follows,
            "like_rate": post_result.like_rate,
            "save_rate": post_result.save_rate,
            "comment_rate": post_result.comment_rate,
            "follow_rate": post_result.follow_rate,
        },
        "relative_lifts": {
            "relative_view_lift": post_result.relative_view_lift,
            "relative_like_lift": post_result.relative_like_lift,
            "relative_save_lift": post_result.relative_save_lift,
            "relative_comment_lift": post_result.relative_comment_lift,
            "relative_follow_lift": post_result.relative_follow_lift,
        },
    }
