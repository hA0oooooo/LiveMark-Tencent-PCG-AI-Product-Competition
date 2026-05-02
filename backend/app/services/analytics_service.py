from collections import defaultdict
from sqlalchemy.orm import Session

from app.exceptions import not_found
from app.repositories import account_repository, asset_repository, historical_post_repository, publish_plan_repository
from app.services import memory_service
from app.utils.metric_utils import compute_lift, compute_rate


def get_account_benchmark(db: Session, account_id: int) -> dict:
    account = account_repository.get(db, account_id)
    if not account:
        raise not_found("未找到账号")
    posts = historical_post_repository.list_by_account(db, account_id)
    return {
        "account_id": account.id,
        "avg_views": account.avg_views,
        "avg_likes": account.avg_likes,
        "avg_saves": account.avg_saves,
        "avg_comments": account.avg_comments,
        "avg_shares": 0,
        "avg_follows": account.avg_follows,
        "avg_like_rate": compute_rate(account.avg_likes, account.avg_views),
        "avg_save_rate": compute_rate(account.avg_saves, account.avg_views),
        "avg_comment_rate": compute_rate(account.avg_comments, account.avg_views),
        "avg_follow_rate": compute_rate(account.avg_follows, account.avg_views),
        "historical_post_count": len(posts),
    }


def get_historical_post_stats(db: Session, account_id: int) -> dict:
    posts = historical_post_repository.list_by_account(db, account_id)
    count = len(posts)
    if not count:
        return {
            "count": 0,
            "avg_views": 0,
            "avg_likes": 0,
            "avg_saves": 0,
            "avg_comments": 0,
            "avg_shares": 0,
            "avg_follows": 0,
            "content_type_performance": [],
        }
    return {
        "count": count,
        "avg_views": sum(p.views for p in posts) / count,
        "avg_likes": sum(p.likes for p in posts) / count,
        "avg_saves": sum(p.saves for p in posts) / count,
        "avg_comments": sum(p.comments for p in posts) / count,
        "avg_shares": sum((getattr(p, "shares", 0) or 0) for p in posts) / count,
        "avg_follows": sum((p.follows or 0) for p in posts) / count if any((p.follows or 0) for p in posts) else 0,
        "content_type_performance": get_content_type_performance(db, account_id),
    }


def get_content_type_performance(db: Session, account_id: int) -> list[dict]:
    posts = historical_post_repository.list_by_account(db, account_id)
    grouped: dict[str, list] = defaultdict(list)
    for post in posts:
        grouped[post.content_type].append(post)
    rows = []
    for content_type, items in grouped.items():
        count = len(items)
        avg_views = sum(p.views for p in items) / count
        avg_likes = sum(p.likes for p in items) / count
        avg_saves = sum(p.saves for p in items) / count
        avg_comments = sum(p.comments for p in items) / count
        avg_shares = sum((getattr(p, "shares", 0) or 0) for p in items) / count
        has_follows = any((p.follows or 0) for p in items)
        avg_follows = sum((p.follows or 0) for p in items) / count if has_follows else 0
        rows.append(
            {
                "content_type": content_type,
                "count": count,
                "avg_views": avg_views,
                "avg_likes": avg_likes,
                "avg_saves": avg_saves,
                "avg_comments": avg_comments,
                "avg_shares": avg_shares,
                "avg_follows": avg_follows,
                "avg_like_rate": compute_rate(avg_likes, avg_views),
                "avg_save_rate": compute_rate(avg_saves, avg_views),
                "avg_comment_rate": compute_rate(avg_comments, avg_views),
                "avg_follow_rate": compute_rate(avg_follows, avg_views),
            }
        )
    return sorted(rows, key=lambda row: (row["avg_follow_rate"], row["avg_comment_rate"], row["avg_save_rate"]), reverse=True)


def get_dashboard_stats(db: Session, account_id: int) -> dict:
    account = account_repository.get(db, account_id)
    if not account:
        raise not_found("未找到账号")
    performance = get_content_type_performance(db, account_id)
    assets = asset_repository.list_assets(db, account_id=account_id)
    plans = publish_plan_repository.list_plans(db, account_id=account_id)
    return {
        "account": account,
        "benchmark": get_account_benchmark(db, account_id),
        "historical_post_count": len(historical_post_repository.list_by_account(db, account_id)),
        "asset_count": len(assets),
        "publish_plan_count": len(plans),
        "best_content_type": performance[0]["content_type"] if performance else None,
        "recent_publish_plans": plans[:5],
        "content_type_performance": performance,
        "growth_insights": get_growth_insights(db, account_id),
    }


def get_growth_insights(db: Session, account_id: int) -> list[str]:
    performance = get_content_type_performance(db, account_id)
    account = account_repository.get(db, account_id)
    profile = memory_service.account_profile_memory(account) if account else {}
    if not performance:
        insights = [
            "当前账号已使用手动基准数据，后续请从素材上传、发布矩阵和复盘数据开始积累真实内容记忆。",
            "复盘时优先观察收藏率、评论率和可选转粉率，并与账号基准对比。",
        ]
        if profile.get("shooting_style_memory"):
            insights.append(f"拍摄风格建议：{profile['shooting_style_memory']}")
        if profile.get("content_direction_memory"):
            insights.append(f"内容方向建议：{profile['content_direction_memory']}")
        return insights
    best = performance[0]
    learning = memory_service.recent_account_learning(db, account_id, limit=3)
    insights = [
        f"{best['content_type']} 当前相对更适合做发布优先级判断。",
        "复盘时优先观察收藏率、评论率和可选转粉率。",
    ]
    if profile.get("shooting_style_memory"):
        insights.append(f"拍摄风格建议：{profile['shooting_style_memory']}")
    if profile.get("content_direction_memory"):
        insights.append(f"内容方向建议：{profile['content_direction_memory']}")
    if learning:
        latest = next((item for item in learning if item.get("account_learning")), learning[0])
        insights.append(f"最近复盘学习：{latest.get('account_learning') or latest.get('next_action')}")
    else:
        insights.append("下一轮增长建议应围绕账号基准中表现更稳定的内容类型展开。")
    return insights


def compare_post_to_baseline(post_metrics: dict, benchmark: dict) -> dict:
    return {
        "relative_view_lift": compute_lift(post_metrics.get("views"), benchmark.get("avg_views")),
        "relative_like_lift": compute_lift(post_metrics.get("likes"), benchmark.get("avg_likes")),
        "relative_save_lift": compute_lift(post_metrics.get("saves"), benchmark.get("avg_saves")),
        "relative_comment_lift": compute_lift(post_metrics.get("comments"), benchmark.get("avg_comments")),
        "relative_follow_lift": compute_lift(post_metrics.get("follows") or 0, benchmark.get("avg_follows")),
    }
