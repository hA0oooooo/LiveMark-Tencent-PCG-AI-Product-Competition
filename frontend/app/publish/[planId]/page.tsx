"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { getPublishPlan, updatePublishPlan } from "@/lib/api";
import type { PublishPlan } from "@/lib/types";
import { targetMetricLabels } from "@/lib/constants";
import { Button } from "@/components/ui/Button";
import { Card, CardTitle } from "@/components/ui/Card";
import { ErrorState, LoadingState } from "@/components/shared/State";

export default function PublishDetailPage() {
  const { planId } = useParams<{ planId: string }>();
  const [plan, setPlan] = useState<PublishPlan | null>(null);
  const [error, setError] = useState("");

  const load = () => getPublishPlan(Number(planId)).then(setPlan).catch((err) => setError(err.message));
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
