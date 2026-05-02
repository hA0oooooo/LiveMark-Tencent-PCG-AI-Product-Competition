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
            "interaction_score": float(analysis.get("interaction_score", 50)),
            "emotion_score": float(analysis.get("emotion_score", 50)),
            "rarity_score": float(analysis.get("rarity_score", 50)),
            "title_cover_score": float(analysis.get("cover_potential_score", 50)),
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
