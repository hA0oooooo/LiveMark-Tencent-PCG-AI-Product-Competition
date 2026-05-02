from functools import lru_cache
import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


class Settings:
    APP_NAME = os.getenv("APP_NAME", "LiveMark")
    ENV = os.getenv("ENV", "development")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app/data/livemark.db")

    DATA_DIR = Path(os.getenv("DATA_DIR", "app/data"))
    UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "app/data/uploads"))
    FRAME_DIR = Path(os.getenv("FRAME_DIR", "app/data/frames"))
    CLIP_DIR = Path(os.getenv("CLIP_DIR", "app/data/clips"))

    MODELSCOPE_API_KEY = os.getenv("MODELSCOPE_API_KEY", "")
    MODELSCOPE_BASE_URL = os.getenv("MODELSCOPE_BASE_URL", "https://api-inference.modelscope.cn/v1")
    VISION_MODEL_NAME = os.getenv("VISION_MODEL_NAME", "")
    TEXT_MODEL_NAME = os.getenv("TEXT_MODEL_NAME", "")

    FRAME_SAMPLE_INTERVAL_SECONDS = int(os.getenv("FRAME_SAMPLE_INTERVAL_SECONDS", "2"))
    MAX_SELECTED_FRAMES = int(os.getenv("MAX_SELECTED_FRAMES", "8"))
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
