export type Account = {
  id: number;
  name: string;
  platform: string;
  niche: string;
  target_audience: string;
  style_positioning: string;
  follower_count: number;
  avg_views: number;
  avg_likes: number;
  avg_saves: number;
  avg_comments: number;
  avg_follows: number;
  strategy_summary: string;
  shooting_style_memory: string;
  content_direction_memory: string;
  audience_preference_memory: string;
  negative_lessons: string;
  updated_memory_at: string | null;
  created_at: string;
  updated_at: string;
};

export type AccountBenchmark = {
  account_id: number;
  avg_views: number;
  avg_likes: number;
  avg_saves: number;
  avg_comments: number;
  avg_follows: number;
  avg_like_rate: number;
  avg_save_rate: number;
  avg_comment_rate: number;
  avg_follow_rate: number;
  historical_post_count: number;
};

export type HistoricalPost = {
  id: number;
  account_id: number;
  title: string;
  content_type: string;
  publish_time: string | null;
  views: number;
  likes: number;
  saves: number;
  comments: number;
  follows: number | null;
  has_interaction: boolean;
  has_emotion: boolean;
  has_rare_view: boolean;
  has_cover_text: boolean;
  has_bgm: boolean;
  creator_note: string;
  created_at: string;
};

export type Frame = {
  id: number;
  asset_id: number;
  timestamp: number;
  frame_path: string;
  clarity_score: number;
  is_selected: boolean;
  vl_description: string;
  vl_json: string;
  created_at: string;
};

export type Clip = {
  id: number;
  asset_id: number;
  start_time: number;
  end_time: number;
  cover_frame_path: string;
  clip_type: string;
  clarity_score: number;
  interaction_score: number;
  emotion_score: number;
  rarity_score: number;
  title_cover_score: number;
  account_fit_score: number;
  growth_score: number;
  target_metric: "click" | "save" | "comment" | "follow" | "long_tail";
  ai_reason: string;
  editing_advice: string;
  account_fit_reason: string;
  risk_note: string;
  created_at: string;
};

export type PublishPlan = {
  id: number;
  clip_id: number;
  asset_id: number;
  account_id: number;
  title: string;
  cover_text: string;
  caption: string;
  hashtags: string;
  comment_prompt: string;
  recommended_publish_time: string;
  target_metric: string;
  status: "draft" | "published" | "reviewed";
  ai_strategy: string;
  created_at: string;
  updated_at: string;
};

export type Asset = {
  id: number;
  account_id: number;
  event_name: string;
  scene_type: string;
  target_person: string;
  context_note: string;
  video_path: string;
  duration: number;
  upload_time: string;
  status: "uploaded" | "processing" | "analyzed" | "plan_generated" | "reviewed" | "failed";
  summary: string;
  created_at: string;
  updated_at: string;
  frames?: Frame[];
  clips?: Clip[];
  publish_plans?: PublishPlan[];
};

export type PostResult = {
  id: number;
  publish_plan_id: number;
  actual_publish_time: string | null;
  actual_title: string;
  views: number;
  likes: number;
  saves: number;
  comments: number;
  follows: number | null;
  like_rate: number;
  save_rate: number;
  comment_rate: number;
  follow_rate: number;
  relative_view_lift: number;
  relative_like_lift: number;
  relative_save_lift: number;
  relative_comment_lift: number;
  relative_follow_lift: number;
  ai_review: string;
  next_action: string;
  ai_memory_suggestion: string;
  created_at: string;
};

export type ContentTypePerformance = {
  content_type: string;
  count: number;
  avg_views: number;
  avg_likes: number;
  avg_saves: number;
  avg_comments: number;
  avg_follows: number;
  avg_like_rate: number;
  avg_save_rate: number;
  avg_comment_rate: number;
  avg_follow_rate: number;
};

export type DashboardStats = {
  account: Account;
  benchmark: AccountBenchmark;
  historical_post_count: number;
  asset_count: number;
  publish_plan_count: number;
  best_content_type: string | null;
  recent_publish_plans: PublishPlan[];
  content_type_performance: ContentTypePerformance[];
  growth_insights: string[];
};
