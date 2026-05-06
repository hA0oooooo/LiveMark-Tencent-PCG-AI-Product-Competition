from sqlalchemy.orm import Session

from app.exceptions import not_found
from app.repositories import clip_repository
from app.services import scoring_service


def generate_candidate_clips(asset, frames: list, frame_analyses: list[dict], historical_stats: list[dict]) -> list[dict]:
    candidates = []
    follows_available = scoring_service.follows_available_from_stats(historical_stats)
    selected_frames = [frame for frame in frames if getattr(frame, "is_selected", False)]
    for frame, analysis in zip(selected_frames, frame_analyses):
        scores = {
            "clarity_score": frame.clarity_score,
            "interaction_score": normalize_model_score(analysis.get("interaction_score", 50)),
            "emotion_score": normalize_model_score(analysis.get("emotion_score", 50)),
            "rarity_score": normalize_model_score(analysis.get("rarity_score", 50)),
            "title_cover_score": normalize_model_score(analysis.get("cover_potential_score", 50)),
        }
        clip_type = scoring_service.assign_clip_type(scores, analysis)
        scores["account_fit_score"] = scoring_service.compute_account_fit_score(clip_type, historical_stats)
        target_metric = scoring_service.infer_target_metric(scores, clip_type, follows_available=follows_available)
        scores["growth_score"] = scoring_service.compute_growth_score(scores)
        candidates.append(
            {
                "asset_id": asset.id,
                "start_time": max(0, frame.timestamp - 3),
                "end_time": min(asset.duration or frame.timestamp + 5, frame.timestamp + 5),
                "cover_frame_path": frame.frame_path,
                "clip_type": clip_type,
                "target_metric": target_metric,
                "ai_reason": analysis.get("fan_reaction_hypothesis")
                or scoring_service.explain_growth_score(scores, target_metric),
                "editing_advice": build_editing_advice(frame.timestamp, clip_type, target_metric, analysis),
                "account_fit_reason": build_account_fit_reason(clip_type, scores),
                "risk_note": analysis.get("risk_note", ""),
                **scores,
            }
        )
    ranked = sorted(candidates, key=lambda item: item["growth_score"], reverse=True)[:5]
    return rank_clips(merge_close_clips(ranked))[:3]


def merge_close_clips(candidate_clips: list[dict], min_gap_seconds: int = 5) -> list[dict]:
    if not candidate_clips:
        return []
    clips = sorted(candidate_clips, key=lambda item: item["start_time"])
    merged = [clips[0]]
    for clip in clips[1:]:
        last = merged[-1]
        if clip["start_time"] - last["end_time"] <= min_gap_seconds:
            if clip["growth_score"] > last["growth_score"]:
                clip["start_time"] = min(last["start_time"], clip["start_time"])
                clip["end_time"] = max(last["end_time"], clip["end_time"])
                merged[-1] = clip
            else:
                last["end_time"] = max(last["end_time"], clip["end_time"])
        else:
            merged.append(clip)
    return merged


def create_clip_records(db: Session, asset_id: int, candidate_clips: list[dict]):
    clip_repository.delete_by_asset(db, asset_id)
    return clip_repository.bulk_create(db, candidate_clips)


def list_clips_by_asset(db: Session, asset_id: int):
    return clip_repository.list_by_asset(db, asset_id)


def get_clip(db: Session, clip_id: int):
    clip = clip_repository.get(db, clip_id)
    if not clip:
        raise not_found("未找到候选片段")
    return clip


def rank_clips(clips: list):
    return sorted(clips, key=lambda item: item["growth_score"] if isinstance(item, dict) else item.growth_score, reverse=True)


def normalize_model_score(value) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return 50
    if 0 <= score <= 10:
        score *= 10
    return max(0, min(100, score))


def build_editing_advice(timestamp: float, clip_type: str, target_metric: str, analysis: dict) -> str:
    clip_type_label = clip_type_label_zh(clip_type)
    metric_hint = {
        "click": "把最稀缺的画面放在前 1 秒，封面文字直接点出现场才看到的瞬间。",
        "save": "保留清晰稳定的画面，节奏不要切太碎，适合做可反复看的收藏片段。",
        "comment": "保留人物反应和现场互动，结尾用问题引导评论区讨论。",
        "follow": "突出目标人物状态和人设细节，让观众形成继续关注的理由。",
        "long_tail": "保留现场氛围和完整情绪，让片段适合几天后仍被回看。",
    }
    return (
        f"围绕 {timestamp:.1f}s 附近剪出{clip_type_label}片段。"
        f"{metric_hint.get(target_metric, metric_hint['long_tail'])}"
        f"画面判断：{analysis.get('description', '需人工复核画面重点')}"
    )


def build_account_fit_reason(clip_type: str, scores: dict) -> str:
    clip_type_label = clip_type_label_zh(clip_type)
    return (
        f"该片段被归为{clip_type_label}，账号匹配分 {scores.get('account_fit_score', 0):.1f}。"
        "判断依据来自账号历史内容类型表现、目标粉丝偏好和当前片段互动/情绪/稀缺视角信号。"
    )


def clip_type_label_zh(clip_type: str) -> str:
    labels = {
        "timely": "抢鲜型",
        "interaction": "互动型",
        "high_quality_collection": "高清收藏型",
        "emotion": "情绪氛围型",
        "persona_detail": "人设细节型",
        "long_tail": "长尾现场型",
        "compilation": "合集型",
    }
    return labels.get(clip_type, "现场记录型")
