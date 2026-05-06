from app.utils.metric_utils import compute_rate


def normalize_score(value: float, min_value: float, max_value: float) -> float:
    if max_value <= min_value:
        return 0
    return max(0, min(100, (value - min_value) / (max_value - min_value) * 100))


def compute_clarity_score(raw_clarity: float) -> float:
    return normalize_score(raw_clarity, 0, 800)


def compute_account_fit_score(clip_type: str, historical_stats: list[dict] | None) -> float:
    if not historical_stats:
        return 60
    matched = next((row for row in historical_stats if row.get("content_type") == clip_type), None)
    if not matched:
        return 55
    follow_rate = matched.get("avg_follow_rate") or 0
    comment_rate = matched.get("avg_comment_rate") or 0
    save_rate = matched.get("avg_save_rate") or 0
    like_rate = matched.get("avg_like_rate") or 0
    signal = follow_rate * 1000 if follow_rate else comment_rate * 600 + save_rate * 350 + like_rate * 120
    return max(45, min(92, 55 + signal))


def compute_growth_score(scores: dict, weights: dict | None = None) -> float:
    weights = weights or {
        "interaction_score": 0.25,
        "emotion_score": 0.20,
        "rarity_score": 0.20,
        "clarity_score": 0.15,
        "title_cover_score": 0.10,
        "account_fit_score": 0.10,
    }
    value = sum((scores.get(key) or 0) * weight for key, weight in weights.items())
    return round(max(0, min(100, value)), 2)


def infer_target_metric(scores: dict, clip_type: str, follows_available: bool = True) -> str:
    if scores.get("account_fit_score", 0) >= 72 and scores.get("interaction_score", 0) >= 70:
        return "follow" if follows_available else "comment"
    if scores.get("rarity_score", 0) >= 72 and scores.get("title_cover_score", 0) >= 68:
        return "click"
    if scores.get("interaction_score", 0) >= 70:
        return "comment"
    if scores.get("clarity_score", 0) >= 72:
        return "save"
    if scores.get("emotion_score", 0) >= 68:
        return "long_tail" if clip_type in {"emotion", "long_tail"} else "save"
    return "long_tail"


def assign_clip_type(scores: dict, vl_analysis: dict) -> str:
    suggested = vl_analysis.get("suggested_clip_type")
    allowed = {"timely", "interaction", "high_quality_collection", "emotion", "persona_detail", "long_tail", "compilation"}
    if suggested in allowed and suggested != "long_tail":
        return suggested
    if scores.get("interaction_score", 0) >= 70:
        return "interaction"
    if scores.get("clarity_score", 0) >= 75:
        return "high_quality_collection"
    if scores.get("emotion_score", 0) >= 70:
        return "emotion"
    if scores.get("rarity_score", 0) >= 70:
        return "long_tail"
    return "long_tail"


def explain_growth_score(scores: dict, target_metric: str) -> str:
    strongest = max(scores.items(), key=lambda item: item[1] if isinstance(item[1], (int, float)) else 0)[0]
    metric_map = {
        "click": "点击",
        "save": "收藏",
        "comment": "评论",
        "follow": "转粉",
        "long_tail": "长尾传播",
    }
    return f"该片段的 {strongest} 信号更突出，建议作为面向{metric_map.get(target_metric, '长尾传播')}的内容实验。"


def follows_available_from_stats(historical_stats: list[dict] | None) -> bool:
    return bool(historical_stats and any((row.get("avg_follows") or 0) > 0 for row in historical_stats))
