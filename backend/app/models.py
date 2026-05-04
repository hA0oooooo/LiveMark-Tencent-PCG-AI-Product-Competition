from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def now() -> datetime:
    return datetime.utcnow()


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    platform: Mapped[str] = mapped_column(String(40), default="小红书", nullable=False)
    niche: Mapped[str] = mapped_column(String(200), default="")
    target_audience: Mapped[str] = mapped_column(Text, default="")
    style_positioning: Mapped[str] = mapped_column(Text, default="")
    follower_count: Mapped[int] = mapped_column(Integer, default=0)
    current_note_count: Mapped[int] = mapped_column(Integer, default=0)
    total_likes: Mapped[int] = mapped_column(Integer, default=0)
    total_saves: Mapped[int] = mapped_column(Integer, default=0)
    avg_views: Mapped[float] = mapped_column(Float, default=0)
    avg_likes: Mapped[float] = mapped_column(Float, default=0)
    avg_saves: Mapped[float] = mapped_column(Float, default=0)
    avg_comments: Mapped[float] = mapped_column(Float, default=0)
    avg_follows: Mapped[float] = mapped_column(Float, default=0)
    strategy_summary: Mapped[str] = mapped_column(Text, default="")
    shooting_style_memory: Mapped[str] = mapped_column(Text, default="")
    content_direction_memory: Mapped[str] = mapped_column(Text, default="")
    audience_preference_memory: Mapped[str] = mapped_column(Text, default="")
    negative_lessons: Mapped[str] = mapped_column(Text, default="")
    updated_memory_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)

    historical_posts = relationship("HistoricalPost", back_populates="account", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="account", cascade="all, delete-orphan")


class HistoricalPost(Base):
    __tablename__ = "historical_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    content_type: Mapped[str] = mapped_column(String(40), nullable=False)
    publish_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    views: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    saves: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    shares: Mapped[int] = mapped_column(Integer, default=0)
    follows: Mapped[int | None] = mapped_column(Integer, nullable=True)
    has_interaction: Mapped[bool] = mapped_column(Boolean, default=False)
    has_emotion: Mapped[bool] = mapped_column(Boolean, default=False)
    has_rare_view: Mapped[bool] = mapped_column(Boolean, default=False)
    has_cover_text: Mapped[bool] = mapped_column(Boolean, default=False)
    has_bgm: Mapped[bool] = mapped_column(Boolean, default=False)
    creator_note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

    account = relationship("Account", back_populates="historical_posts")


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False, index=True)
    event_name: Mapped[str] = mapped_column(String(160), nullable=False)
    scene_type: Mapped[str] = mapped_column(String(120), default="")
    target_person: Mapped[str] = mapped_column(String(120), default="")
    context_note: Mapped[str] = mapped_column(Text, default="")
    video_path: Mapped[str] = mapped_column(Text, nullable=False)
    duration: Mapped[float] = mapped_column(Float, default=0)
    upload_time: Mapped[datetime] = mapped_column(DateTime, default=now)
    status: Mapped[str] = mapped_column(String(40), default="uploaded")
    summary: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)

    account = relationship("Account", back_populates="assets")
    frames = relationship("Frame", back_populates="asset", cascade="all, delete-orphan")
    clips = relationship("Clip", back_populates="asset", cascade="all, delete-orphan")
    publish_plans = relationship("PublishPlan", back_populates="asset", cascade="all, delete-orphan")


class Frame(Base):
    __tablename__ = "frames"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False, index=True)
    timestamp: Mapped[float] = mapped_column(Float, nullable=False)
    frame_path: Mapped[str] = mapped_column(Text, nullable=False)
    clarity_score: Mapped[float] = mapped_column(Float, default=0)
    is_selected: Mapped[bool] = mapped_column(Boolean, default=False)
    vl_description: Mapped[str] = mapped_column(Text, default="")
    vl_json: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

    asset = relationship("Asset", back_populates="frames")


class Clip(Base):
    __tablename__ = "clips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False, index=True)
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    cover_frame_path: Mapped[str] = mapped_column(Text, default="")
    clip_type: Mapped[str] = mapped_column(String(40), default="long_tail")
    clarity_score: Mapped[float] = mapped_column(Float, default=0)
    interaction_score: Mapped[float] = mapped_column(Float, default=0)
    emotion_score: Mapped[float] = mapped_column(Float, default=0)
    rarity_score: Mapped[float] = mapped_column(Float, default=0)
    title_cover_score: Mapped[float] = mapped_column(Float, default=0)
    account_fit_score: Mapped[float] = mapped_column(Float, default=0)
    growth_score: Mapped[float] = mapped_column(Float, default=0)
    target_metric: Mapped[str] = mapped_column(String(40), default="long_tail")
    ai_reason: Mapped[str] = mapped_column(Text, default="")
    editing_advice: Mapped[str] = mapped_column(Text, default="")
    account_fit_reason: Mapped[str] = mapped_column(Text, default="")
    risk_note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

    asset = relationship("Asset", back_populates="clips")
    publish_plans = relationship("PublishPlan", back_populates="clip", cascade="all, delete-orphan")


class PublishPlan(Base):
    __tablename__ = "publish_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    clip_id: Mapped[int] = mapped_column(ForeignKey("clips.id"), nullable=False, index=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False, index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    cover_text: Mapped[str] = mapped_column(String(160), default="")
    caption: Mapped[str] = mapped_column(Text, default="")
    hashtags: Mapped[str] = mapped_column(Text, default="")
    comment_prompt: Mapped[str] = mapped_column(Text, default="")
    recommended_publish_time: Mapped[str] = mapped_column(String(120), default="")
    target_metric: Mapped[str] = mapped_column(String(40), default="long_tail")
    status: Mapped[str] = mapped_column(String(40), default="draft")
    ai_strategy: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)

    clip = relationship("Clip", back_populates="publish_plans")
    asset = relationship("Asset", back_populates="publish_plans")


class PostResult(Base):
    __tablename__ = "post_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    publish_plan_id: Mapped[int] = mapped_column(ForeignKey("publish_plans.id"), nullable=False, unique=True, index=True)
    historical_post_id: Mapped[int | None] = mapped_column(ForeignKey("historical_posts.id"), nullable=True, index=True)
    actual_publish_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    actual_title: Mapped[str] = mapped_column(String(240), default="")
    views: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    saves: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    follows: Mapped[int | None] = mapped_column(Integer, nullable=True)
    like_rate: Mapped[float] = mapped_column(Float, default=0)
    save_rate: Mapped[float] = mapped_column(Float, default=0)
    comment_rate: Mapped[float] = mapped_column(Float, default=0)
    follow_rate: Mapped[float] = mapped_column(Float, default=0)
    relative_view_lift: Mapped[float] = mapped_column(Float, default=0)
    relative_like_lift: Mapped[float] = mapped_column(Float, default=0)
    relative_save_lift: Mapped[float] = mapped_column(Float, default=0)
    relative_comment_lift: Mapped[float] = mapped_column(Float, default=0)
    relative_follow_lift: Mapped[float] = mapped_column(Float, default=0)
    ai_review: Mapped[str] = mapped_column(Text, default="")
    next_action: Mapped[str] = mapped_column(Text, default="")
    ai_memory_suggestion: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
