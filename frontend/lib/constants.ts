export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export const contentTypeLabels: Record<string, string> = {
  timely: "抢鲜型",
  interaction: "互动型",
  high_quality_collection: "高清收藏型",
  emotion: "情绪氛围型",
  persona_detail: "人设细节型",
  long_tail: "长尾考古型",
  compilation: "合集型"
};

export const targetMetricLabels: Record<string, string> = {
  click: "点击",
  save: "收藏",
  comment: "评论",
  follow: "转粉",
  long_tail: "长尾"
};

export const assetStatusLabels: Record<string, string> = {
  uploaded: "待分析",
  processing: "分析中",
  analyzed: "已分析",
  plan_generated: "已生成发布矩阵",
  reviewed: "已复盘",
  failed: "分析失败"
};
