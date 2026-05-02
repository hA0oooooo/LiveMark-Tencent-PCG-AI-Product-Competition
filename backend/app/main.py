from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.routes import accounts, analytics, assets, clips, historical_posts, post_results, publish_plans
from app.utils.file_utils import ensure_dir


def include_routers(app: FastAPI) -> None:
    app.include_router(accounts.router)
    app.include_router(historical_posts.router)
    app.include_router(assets.router)
    app.include_router(clips.router)
    app.include_router(publish_plans.router)
    app.include_router(post_results.router)
    app.include_router(analytics.router)


def configure_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_ORIGIN, "http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def mount_static_files(app: FastAPI) -> None:
    ensure_dir(settings.UPLOAD_DIR)
    ensure_dir(settings.FRAME_DIR)
    ensure_dir(settings.CLIP_DIR)
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
    app.mount("/frames", StaticFiles(directory=settings.FRAME_DIR), name="frames")
    app.mount("/clips", StaticFiles(directory=settings.CLIP_DIR), name="clips")


def create_app() -> FastAPI:
    init_db()
    app = FastAPI(title=settings.APP_NAME)
    configure_cors(app)
    include_routers(app)
    mount_static_files(app)

    @app.get("/api/health")
    def health():
        return {"status": "ok", "app": settings.APP_NAME}

    return app


app = create_app()
