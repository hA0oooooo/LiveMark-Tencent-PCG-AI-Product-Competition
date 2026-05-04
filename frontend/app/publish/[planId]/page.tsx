"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { getClip, getPublishPlan, updatePublishPlan } from "@/lib/api";
import type { Clip, PublishPlan } from "@/lib/types";
import { targetMetricLabels } from "@/lib/constants";
import { formatScore, formatTimeRange } from "@/lib/format";
import { mediaUrl } from "@/lib/utils";
import { Button } from "@/components/ui/Button";
import { Card, CardTitle } from "@/components/ui/Card";
import { ErrorState, LoadingState } from "@/components/shared/State";

export default function PublishDetailPage() {
  const { planId } = useParams<{ planId: string }>();
  const [plan, setPlan] = useState<PublishPlan | null>(null);
  const [clip, setClip] = useState<Clip | null>(null);
  const [error, setError] = useState("");

  const load = () =>
    getPublishPlan(Number(planId))
      .then(async (item) => {
        setPlan(item);
        setClip(await getClip(item.clip_id));
      })
      .catch((err) => setError(err.message));
  useEffect(() => { load(); }, [planId]);

  async function markPublished() {
    if (!plan) return;
    setPlan(await updatePublishPlan(plan.id, { status: "published" }));
  }

  if (error) return <ErrorState message={error} />;
  if (!plan) return <LoadingState text="正在加载发布计划" />;

  return (
    <div className="page-grid">
      <div>
        <h1 className="text-2xl font-semibold">发布计划详情</h1>
        <p className="mt-1 text-sm text-muted">目标指标：{targetMetricLabels[plan.target_metric] || plan.target_metric}</p>
      </div>
      <Card>
        <CardTitle>{plan.title}</CardTitle>
        {clip && (
          <div className="mb-5 grid gap-4 rounded-md border border-line bg-surface p-4 md:grid-cols-[260px_1fr]">
            <img src={mediaUrl(clip.cover_frame_path)} alt="" className="aspect-video w-full rounded object-cover" />
            <div className="grid gap-2 text-sm">
              <div className="font-medium text-ink">推荐封面帧</div>
              <div className="text-muted">发布计划默认使用候选片段的代表帧作为封面参考，实际发布时可以按这张图补充封面文案。</div>
              <div>片段时间：{formatTimeRange(clip.start_time, clip.end_time)}</div>
              <div>涨粉机会评分：{formatScore(clip.growth_score)} / 100</div>
            </div>
          </div>
        )}
        <div className="grid gap-4 text-sm">
          <Block label="封面文案" value={plan.cover_text} />
          <Block label="正文 caption" value={plan.caption} />
          <Block label="标签" value={plan.hashtags} />
          <Block label="评论引导" value={plan.comment_prompt} />
          <Block label="推荐发布时间" value={plan.recommended_publish_time} />
          <Block label="AI 策略说明" value={plan.ai_strategy} />
        </div>
        <div className="mt-5 flex gap-2">
          {plan.status === "draft" && <Button onClick={markPublished}>标记为已发布</Button>}
          <Link href={`/review?planId=${plan.id}`}><Button variant="secondary">进入复盘</Button></Link>
        </div>
      </Card>
    </div>
  );
}

function Block({ label, value }: { label: string; value: string }) {
  return <div><div className="text-xs text-muted">{label}</div><div className="mt-1 rounded-md bg-surface p-3">{value || "暂无"}</div></div>;
}
