from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


ContentType = Literal[
    "timely",
    "interaction",
    "high_quality_collection",
    "emotion",
    "persona_detail",
    "long_tail",
    "compilation",
]
AssetStatus = Literal["uploaded", "processing", "analyzed", "plan_generated", "reviewed", "failed"]
PlanStatus = Literal["draft", "published", "reviewed"]
TargetMetric = Literal["click", "save", "comment", "follow", "long_tail"]


class AccountCreate(BaseModel):
    name: str
    platform: str = "小红书"
    niche: str = ""
    target_audience: str = ""
    style_positioning: str = ""
    follower_count: int = 0
    current_note_count: int = 0
    total_likes: int = 0
    total_saves: int = 0
    strategy_summary: str = ""
    shooting_style_memory: str = ""
    content_direction_memory: str = ""
    audience_preference_memory: str = ""
    negative_lessons: str = ""


class AccountUpdate(BaseModel):
    name: str | None = None
    niche: str | None = None
    target_audience: str | None = None
    style_positioning: str | None = None
    follower_count: int | None = None
    current_note_count: int | None = None
    total_likes: int | None = None
    total_saves: int | None = None
    strategy_summary: str | None = None
    shooting_style_memory: str | None = None
    content_direction_memory: str | None = None
    audience_preference_memory: str | None = None
    negative_lessons: str | None = None


class AccountRead(AccountCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    avg_views: float
    avg_likes: float
    avg_saves: float
    avg_comments: float
    avg_follows: float
    strategy_summary: str
    shooting_style_memory: str
    content_direction_memory: str
    audience_preference_memory: str
    negative_lessons: str
    updated_memory_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class AccountBenchmarkRead(BaseModel):
    account_id: int
    avg_views: float
    avg_likes: float
    avg_saves: float
    avg_comments: float
    avg_shares: float = 0
    avg_follows: float
    avg_like_rate: float = 0
    avg_save_rate: float = 0
    avg_comment_rate: float = 0
    avg_follow_rate: float = 0
    historical_post_count: int = 0


class HistoricalPostCreate(BaseModel):
    title: str
    content_type: ContentType
    publish_time: datetime | None = None
    views: int = 0
    likes: int = 0
    saves: int = 0
    comments: int = 0
    shares: int = 0
    has_interaction: bool = False
    has_emotion: bool = False
    has_rare_view: bool = False
    has_cover_text: bool = False
    has_bgm: bool = False


class HistoricalPostRead(HistoricalPostCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    created_at: datetime


class HistoricalPostBulkCreate(BaseModel):
    posts: list[HistoricalPostCreate]


class FrameRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    timestamp: float
    frame_path: str
    clarity_score: float
    is_selected: bool
    vl_description: str
    vl_json: str
    created_at: datetime


class ClipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    start_time: float
    end_time: float
    cover_frame_path: str
    clip_type: str
    clarity_score: float
    interaction_score: float
    emotion_score: float
    rarity_score: float
    title_cover_score: float
    account_fit_score: float
    growth_score: float
    target_metric: TargetMetric
    ai_reason: str
    editing_advice: str
    account_fit_reason: str
    risk_note: str
    created_at: datetime


class AssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    event_name: str
    scene_type: str
    target_person: str
    context_note: str
    video_path: str
    duration: float
    upload_time: datetime
    status: AssetStatus
    summary: str
    created_at: datetime
    updated_at: datetime


class AssetDetailRead(AssetRead):
    frames: list[FrameRead] = []
    clips: list[ClipRead] = []
    publish_plans: list["PublishPlanRead"] = []


class AssetUploadResponse(BaseModel):
    asset: AssetRead
    message: str


class AssetAnalysisResponse(BaseModel):
    asset: AssetDetailRead
    message: str


class PublishPlanUpdate(BaseModel):
    title: str | None = None
    cover_text: str | None = None
    caption: str | None = None
    hashtags: str | list[str] | None = None
    comment_prompt: str | None = None
    recommended_publish_time: str | None = None
    target_metric: TargetMetric | None = None
    status: PlanStatus | None = None
    ai_strategy: str | None = None


class PublishPlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    clip_id: int
    asset_id: int
    account_id: int
    title: str
    cover_text: str
    caption: str
    hashtags: str
    comment_prompt: str
    recommended_publish_time: str
    target_metric: TargetMetric
    status: PlanStatus
    ai_strategy: str
    created_at: datetime
    updated_at: datetime


class PostResultCreate(BaseModel):
    publish_plan_id: int
    actual_publish_time: datetime | None = None
    actual_title: str = ""
    views: int = Field(ge=0)
    likes: int = Field(ge=0)
    saves: int = Field(ge=0)
    comments: int = Field(ge=0)
    follows: int | None = Field(default=None, ge=0)


class PostResultRead(PostResultCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    like_rate: float
    save_rate: float
    comment_rate: float
    follow_rate: float
    relative_view_lift: float
    relative_like_lift: float
    relative_save_lift: float
    relative_comment_lift: float
    relative_follow_lift: float
    ai_review: str
    next_action: str
    ai_memory_suggestion: str
    created_at: datetime


class ContentTypePerformanceRead(BaseModel):
    content_type: str
    count: int
    avg_views: float
    avg_likes: float
    avg_saves: float
    avg_comments: float
    avg_shares: float = 0
    avg_follows: float
    avg_like_rate: float
    avg_save_rate: float
    avg_comment_rate: float
    avg_follow_rate: float


class DashboardStatsRead(BaseModel):
    account: AccountRead
    benchmark: AccountBenchmarkRead
    historical_post_count: int
    asset_count: int
    publish_plan_count: int
    best_content_type: str | None = None
    recent_publish_plans: list[PublishPlanRead] = []
    content_type_performance: list[ContentTypePerformanceRead] = []
    growth_insights: list[str] = []


class HistoricalPostStatsRead(BaseModel):
    count: int
    avg_views: float
    avg_likes: float
    avg_saves: float
    avg_comments: float
    avg_shares: float = 0
    avg_follows: float
    content_type_performance: list[ContentTypePerformanceRead]


class GrowthInsightsRead(BaseModel):
    insights: list[str]


class ErrorRead(BaseModel):
    detail: str


AssetDetailRead.model_rebuild()
