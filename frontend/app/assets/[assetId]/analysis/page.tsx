"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart, ResponsiveContainer } from "recharts";
import { getAsset } from "@/lib/api";
import type { Asset } from "@/lib/types";
import { targetMetricLabels } from "@/lib/constants";
import { formatScore, formatTimeRange } from "@/lib/format";
import { mediaUrl, parseJsonText } from "@/lib/utils";
import { Card, CardTitle } from "@/components/ui/Card";
import { ErrorState, LoadingState } from "@/components/shared/State";

export default function AnalysisPage() {
  const { assetId } = useParams<{ assetId: string }>();
  const [asset, setAsset] = useState<Asset | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getAsset(Number(assetId)).then(setAsset).catch((err) => setError(err.message));
  }, [assetId]);

  if (error) return <ErrorState message={error} />;
  if (!asset) return <LoadingState text="正在加载素材分析" />;

  return (
    <div className="page-grid">
      <div>
        <h1 className="text-2xl font-semibold">素材分析</h1>
        <p className="mt-1 text-sm text-muted">{asset.event_name} 的关键帧理解、候选片段和涨粉机会评分。</p>
      </div>
      <Card>
        <CardTitle>原视频</CardTitle>
        <video src={mediaUrl(asset.video_path)} controls className="aspect-video w-full rounded-md bg-black" />
      </Card>
      <Card>
        <CardTitle>关键帧网格</CardTitle>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {(asset.frames || []).filter((frame) => frame.is_selected).map((frame) => {
            const parsed = parseJsonText<Record<string, unknown>>(frame.vl_json, {});
            return (
              <div key={frame.id} className="rounded-md border border-line bg-surface p-3">
                <img src={mediaUrl(frame.frame_path)} alt="" className="aspect-video w-full rounded object-cover" />
                <div className="mt-2 text-sm font-medium">{frame.timestamp.toFixed(1)}s · 清晰度 {formatScore(frame.clarity_score)}</div>
                <p className="mt-1 text-sm text-muted">{frame.vl_description || String(parsed.description || "暂无描述")}</p>
              </div>
            );
          })}
        </div>
      </Card>
      <Card>
        <CardTitle>候选片段卡片</CardTitle>
        <div className="grid gap-4">
          {(asset.clips || []).map((clip) => (
            <div key={clip.id} className="grid gap-4 rounded-md border border-line p-4 lg:grid-cols-[320px_1fr]">
              <div>
                <img src={mediaUrl(clip.cover_frame_path)} alt="" className="aspect-video w-full rounded object-cover" />
                <div className="mt-3 text-sm text-muted">{formatTimeRange(clip.start_time, clip.end_time)}</div>
                <div className="mt-2 flex items-end gap-2">
                  <div className="text-3xl font-semibold text-brand">{formatScore(clip.growth_score)}</div>
                  <div className="pb-1 text-sm text-muted">/ 100</div>
                </div>
                <div className="text-sm text-muted">涨粉机会评分，满分 100</div>
                <div className="mt-3 h-52 rounded-md bg-white p-2">
                  <ScoreRadar clip={clip} />
                </div>
                <div className="mt-2 rounded-md bg-surface px-3 py-2 text-sm">目标指标：{targetMetricLabels[clip.target_metric]}</div>
              </div>
              <div className="grid gap-3 md:grid-cols-2">
                <InfoBlock title="AI 推荐理由" text={clip.ai_reason || "暂无"} />
                <InfoBlock title="剪辑建议" text={clip.editing_advice || "暂无"} />
                <InfoBlock title="账号匹配" text={clip.account_fit_reason || "暂无"} />
                <InfoBlock title="风险提示" text={clip.risk_note || "暂无"} muted />
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

function ScoreRadar({ clip }: { clip: NonNullable<Asset["clips"]>[number] }) {
  const data = [
    { metric: "互动", value: clip.interaction_score },
    { metric: "情绪", value: clip.emotion_score },
    { metric: "稀缺", value: clip.rarity_score },
    { metric: "清晰", value: clip.clarity_score },
    { metric: "封面", value: clip.title_cover_score },
    { metric: "匹配", value: clip.account_fit_score },
  ];
  return (
    <ResponsiveContainer width="100%" height="100%">
      <RadarChart data={data} outerRadius="72%">
        <PolarGrid stroke="#e5e7eb" />
        <PolarAngleAxis dataKey="metric" tick={{ fill: "#64748b", fontSize: 12 }} />
        <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} axisLine={false} />
        <Radar dataKey="value" stroke="#e11d48" fill="#e11d48" fillOpacity={0.22} strokeWidth={2} />
      </RadarChart>
    </ResponsiveContainer>
  );
}

function InfoBlock({ title, text, muted = false }: { title: string; text: string; muted?: boolean }) {
  return (
    <div className="rounded-md bg-surface p-3">
      <div className="text-xs font-medium text-muted">{title}</div>
      <p className={`mt-1 text-sm ${muted ? "text-muted" : "text-ink"}`}>{text}</p>
    </div>
  );
}
