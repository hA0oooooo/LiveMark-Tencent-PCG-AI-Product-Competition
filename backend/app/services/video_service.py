import shutil
from pathlib import Path

try:
    import cv2
except Exception:  # pragma: no cover
    cv2 = None

from fastapi import UploadFile

from app.utils.file_utils import ensure_dir, generate_unique_filename
from app.utils.video_utils import run_ffmpeg_command, run_ffprobe_duration


def save_uploaded_video(file: UploadFile, upload_dir: str | Path) -> str:
    ensure_dir(upload_dir)
    filename = generate_unique_filename(file.filename or "upload.mp4")
    path = Path(upload_dir) / filename
    with path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return str(path)


def get_video_duration(video_path: str) -> float:
    try:
        return run_ffprobe_duration(video_path)
    except Exception:
        if cv2 is not None:
            cap = cv2.VideoCapture(video_path)
            if cap.isOpened():
                fps = cap.get(cv2.CAP_PROP_FPS) or 0
                frames = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
                cap.release()
                if fps > 0:
                    return float(frames / fps)
        return 0


def extract_frames(video_path: str, output_dir: str | Path, interval_seconds: int = 2) -> list[dict]:
    ensure_dir(output_dir)
    duration = get_video_duration(video_path)
    timestamps = []
    if duration <= 0:
        timestamps = [0]
    else:
        cursor = 0.0
        while cursor <= duration:
            timestamps.append(cursor)
            cursor += max(1, interval_seconds)
    frames = []
    for index, timestamp in enumerate(timestamps):
        frame_path = Path(output_dir) / f"frame-{index:03d}.jpg"
        try:
            run_ffmpeg_command(["ffmpeg", "-y", "-ss", str(timestamp), "-i", video_path, "-frames:v", "1", str(frame_path)])
            if frame_path.exists() and frame_path.stat().st_size > 0:
                frames.append({"timestamp": timestamp, "frame_path": str(frame_path), "clarity_score": calculate_clarity_score(frame_path)})
        except Exception:
            continue
    if frames:
        return frames
    return extract_frames_with_opencv(video_path, output_dir, interval_seconds)


def extract_frames_with_opencv(video_path: str, output_dir: str | Path, interval_seconds: int = 2) -> list[dict]:
    if cv2 is None:
        return []
    ensure_dir(output_dir)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    total = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
    duration = total / fps if fps else 0
    frames = []
    timestamp = 0.0
    index = 0
    while timestamp <= max(duration, 0):
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
        ok, image = cap.read()
        if not ok:
            break
        frame_path = Path(output_dir) / f"frame-{index:03d}.jpg"
        cv2.imwrite(str(frame_path), image)
        frames.append({"timestamp": timestamp, "frame_path": str(frame_path), "clarity_score": calculate_clarity_score(frame_path)})
        index += 1
        timestamp += max(1, interval_seconds)
        if duration <= 0:
            break
    cap.release()
    return frames


def extract_key_frames(video_path: str, output_dir: str | Path, max_frames: int) -> list[dict]:
    frames = extract_frames(video_path, output_dir)
    return select_representative_frames(frames, max_frames)


def calculate_clarity_score(image_path: str | Path) -> float:
    if cv2 is None:
        return 50
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        return 0
    raw = float(cv2.Laplacian(image, cv2.CV_64F).var())
    return max(0, min(100, raw / 800 * 100))


def select_representative_frames(frames: list[dict], max_count: int) -> list[dict]:
    if len(frames) <= max_count:
        return sorted(frames, key=lambda frame: frame["timestamp"])
    ordered = sorted(frames, key=lambda frame: frame.get("clarity_score", 0), reverse=True)[: max_count * 2]
    selected = sorted(ordered, key=lambda frame: frame["timestamp"])
    if len(selected) <= max_count:
        return selected
    step = len(selected) / max_count
    return [selected[int(i * step)] for i in range(max_count)]


def generate_thumbnail(frame_path: str, output_path: str) -> str:
    target = Path(output_path)
    ensure_dir(target.parent)
    shutil.copyfile(frame_path, target)
    return str(target)
