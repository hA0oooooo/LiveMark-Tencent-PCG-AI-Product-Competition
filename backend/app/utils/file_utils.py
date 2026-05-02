from pathlib import Path
import re
import uuid


ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".avi", ".webm"}


def ensure_dir(path: str | Path) -> Path:
    target = Path(path)
    target.mkdir(parents=True, exist_ok=True)
    return target


def safe_filename(filename: str) -> str:
    stem = Path(filename).stem or "upload"
    suffix = Path(filename).suffix.lower()
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "-", stem).strip("-") or "upload"
    return f"{cleaned}{suffix}"


def generate_unique_filename(filename: str) -> str:
    safe = safe_filename(filename)
    return f"{uuid.uuid4().hex[:12]}-{safe}"


def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def is_allowed_video_file(filename: str) -> bool:
    return get_file_extension(filename) in ALLOWED_VIDEO_EXTENSIONS
