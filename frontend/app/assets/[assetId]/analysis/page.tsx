"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
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
        <div className="grid gap-4 md:grid-cols-3">
          {(asset.clips || []).map((clip) => (
            <div key={clip.id} className="rounded-md border border-line p-4">
              <img src={mediaUrl(clip.cover_frame_path)} alt="" className="aspect-video w-full rounded object-cover" />
              <div className="mt-3 text-sm text-muted">{formatTimeRange(clip.start_time, clip.end_time)}</div>
              <div className="mt-1 text-2xl font-semibold text-brand">{formatScore(clip.growth_score)}</div>
              <div className="text-sm text-muted">涨粉机会评分</div>
              <div className="mt-2 text-sm">目标指标：{targetMetricLabels[clip.target_metric]}</div>
              <p className="mt-2 text-sm text-muted">{clip.ai_reason}</p>
              {clip.editing_advice && <p className="mt-2 rounded bg-surface p-2 text-xs text-ink">剪辑建议：{clip.editing_advice}</p>}
              {clip.account_fit_reason && <p className="mt-2 rounded bg-surface p-2 text-xs text-muted">账号匹配：{clip.account_fit_reason}</p>}
              {clip.risk_note && <p className="mt-2 rounded bg-surface p-2 text-xs text-muted">风险提示：{clip.risk_note}</p>}
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
