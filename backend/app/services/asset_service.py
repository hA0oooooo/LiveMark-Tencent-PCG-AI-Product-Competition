import json
from pathlib import Path
from sqlalchemy.orm import Session

from fastapi import UploadFile

from app.config import settings
from app.exceptions import bad_request, not_found
from app.repositories import asset_repository, frame_repository
from app.services import account_service, analytics_service, clip_service, modelscope_service, video_service
from app.utils.file_utils import ensure_dir, is_allowed_video_file


def create_asset_from_upload(
    db: Session,
    file: UploadFile,
    account_id: int,
    event_name: str,
    scene_type: str,
    target_person: str,
):
    account_service.get_account(db, account_id)
    if not is_allowed_video_file(file.filename or ""):
        raise bad_request("仅支持 mp4、mov、m4v、avi、webm 视频文件")
    video_path = video_service.save_uploaded_video(file, settings.UPLOAD_DIR)
    duration = video_service.get_video_duration(video_path)
    return asset_repository.create(
        db,
        {
            "account_id": account_id,
            "event_name": event_name,
            "scene_type": scene_type,
            "target_person": target_person,
            "video_path": video_path,
            "duration": duration,
            "status": "uploaded",
            "summary": "",
        },
    )


def list_assets(db: Session, account_id: int | None = None, status: str | None = None):
    return asset_repository.list_assets(db, account_id=account_id, status=status)


def get_asset(db: Session, asset_id: int):
    asset = asset_repository.get(db, asset_id)
    if not asset:
        raise not_found("未找到素材")
    return asset


def get_asset_detail(db: Session, asset_id: int):
    asset = asset_repository.get_detail(db, asset_id)
    if not asset:
        raise not_found("未找到素材")
    return asset


def analyze_asset(db: Session, asset_id: int):
    asset = get_asset(db, asset_id)
    account = account_service.get_account(db, asset.account_id)
    try:
        asset_repository.update(db, asset, {"status": "processing", "summary": ""})
        frame_repository.delete_by_asset(db, asset_id)
        frame_output_dir = ensure_dir(Path(settings.FRAME_DIR) / f"asset-{asset_id}")
        extracted = video_service.extract_frames(asset.video_path, frame_output_dir, settings.FRAME_SAMPLE_INTERVAL_SECONDS)
        if not extracted:
            raise RuntimeError("抽帧失败，请确认 ffmpeg 可用且视频文件有效")
        selected = video_service.select_representative_frames(extracted, settings.MAX_SELECTED_FRAMES)
        selected_paths = {item["frame_path"] for item in selected}
        frames = frame_repository.bulk_create(
            db,
            [
                {
                    "asset_id": asset_id,
                    "timestamp": item["timestamp"],
                    "frame_path": item["frame_path"],
                    "clarity_score": item["clarity_score"],
                    "is_selected": item["frame_path"] in selected_paths,
                }
                for item in extracted
            ],
        )
        selected_frames = [frame for frame in frames if frame.is_selected]
        context_base = {
            "platform": "小红书",
            "scene_type": asset.scene_type,
            "target_person": asset.target_person,
            "account_positioning": account.style_positioning,
            "target_audience": account.target_audience,
        }
        analyses = []
        for frame in selected_frames:
            analysis = modelscope_service.analyze_frame_with_qwen_vl(
                frame.frame_path,
                {**context_base, "frame_timestamp": frame.timestamp},
            )
            analyses.append(analysis)
            frame_repository.update(
                db,
                frame,
                {
                    "vl_description": analysis.get("description", ""),
                    "vl_json": json.dumps(analysis, ensure_ascii=False),
                },
            )
        historical_stats = analytics_service.get_content_type_performance(db, asset.account_id)
        candidates = clip_service.generate_candidate_clips(asset, selected_frames, analyses, historical_stats)
        clips = clip_service.create_clip_records(db, asset_id, candidates)
        summary = f"已完成 {len(frames)} 张抽帧、{len(selected_frames)} 张关键帧分析，生成 {len(clips)} 个候选片段。"
        asset_repository.update(db, asset, {"status": "analyzed", "summary": summary})
        return get_asset_detail(db, asset_id)
    except Exception as exc:
        mark_asset_failed(db, asset_id, str(exc))
        raise bad_request(f"素材分析失败：{exc}")


def mark_asset_failed(db: Session, asset_id: int, error_message: str):
    asset = get_asset(db, asset_id)
    return asset_repository.update(db, asset, {"status": "failed", "summary": error_message})
