"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { getPostResult, integratePostResultMemory } from "@/lib/api";
import type { PostResult } from "@/lib/types";
import { formatNumber, formatRate } from "@/lib/format";
import { parseJsonText } from "@/lib/utils";
import { Card, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { ErrorState, LoadingState } from "@/components/shared/State";

export default function ReviewDetailPage() {
  const { postResultId } = useParams<{ postResultId: string }>();
  const [result, setResult] = useState<PostResult | null>(null);
  const [error, setError] = useState("");
  const [integrating, setIntegrating] = useState(false);
  const [integratedMessage, setIntegratedMessage] = useState("");

  useEffect(() => {
    getPostResult(Number(postResultId)).then(setResult).catch((err) => setError(err.message));
  }, [postResultId]);

  if (error) return <ErrorState message={error} />;
  if (!result) return <LoadingState text="正在加载复盘详情" />;

  const review = parseJsonText<Record<string, string | string[]>>(result.ai_review, {});
  const memorySuggestion = parseJsonText<Record<string, string>>(result.ai_memory_suggestion, {});

  async function integrateMemory() {
    if (!result) return;
    setIntegrating(true);
    setError("");
    setIntegratedMessage("");
    try {
      await integratePostResultMemory(result.id);
      setIntegratedMessage("已整合到账号长期记忆，Dashboard 的下一轮增长建议会基于新记忆更新。");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setIntegrating(false);
    }
  }

  return (
    <div className="page-grid">
      <div>
        <h1 className="text-2xl font-semibold">复盘详情</h1>
        <p className="mt-1 text-sm text-muted">基于账号基准对比发布后表现，形成下一轮增长建议。</p>
      </div>
      <div className="grid gap-4 md:grid-cols-4">
        <Metric label="浏览" value={formatNumber(result.views)} />
        <Metric label="点赞率" value={formatRate(result.like_rate)} />
        <Metric label="收藏率" value={formatRate(result.save_rate)} />
        <Metric label="评论率" value={formatRate(result.comment_rate)} />
      </div>
      <Card>
        <CardTitle>相对账号基准表现</CardTitle>
        <div className="grid gap-3 md:grid-cols-5">
          <Metric label="浏览提升" value={`${result.relative_view_lift.toFixed(2)}x`} />
          <Metric label="点赞提升" value={`${result.relative_like_lift.toFixed(2)}x`} />
          <Metric label="收藏提升" value={`${result.relative_save_lift.toFixed(2)}x`} />
          <Metric label="评论提升" value={`${result.relative_comment_lift.toFixed(2)}x`} />
          <Metric label="转粉提升" value={result.follows ? `${result.relative_follow_lift.toFixed(2)}x` : "暂无"} />
        </div>
      </Card>
      <Card>
        <CardTitle>AI 复盘报告</CardTitle>
        <div className="grid gap-3 text-sm">
          <Block label="表现总结" value={String(review.summary || "")} />
          <Block label="最强信号" value={String(review.best_signal || "")} />
          <Block label="最弱信号" value={String(review.weak_signal || "")} />
          <Block label="是否服务涨粉与原因" value={String(review.growth_reason || "")} />
          <Block label="下一条内容建议" value={String(review.next_action || result.next_action)} />
          <Block label="下一轮内容实验" value={Array.isArray(review.next_content_experiments) ? review.next_content_experiments.join(" / ") : ""} />
          <Block label="账号学习结论" value={String(review.account_learning || "")} />
        </div>
      </Card>
      <Card>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <CardTitle>账号长期记忆更新建议</CardTitle>
            <p className="mt-1 text-sm text-muted">确认后可把当前账号记忆和本次建议交给 AI 重新整理，写回账号长期记忆。</p>
          </div>
          <Button onClick={integrateMemory} disabled={integrating}>
            {integrating ? "整合中" : "整合长期记忆"}
          </Button>
        </div>
        {integratedMessage && <div className="mt-3 rounded-md bg-surface p-3 text-sm text-ink">{integratedMessage}</div>}
        <div className="grid gap-3 text-sm">
          <Block label="增长策略摘要" value={memorySuggestion.strategy_summary || ""} />
          <Block label="拍摄风格记忆" value={memorySuggestion.shooting_style_memory || ""} />
          <Block label="内容方向记忆" value={memorySuggestion.content_direction_memory || ""} />
          <Block label="目标粉丝偏好" value={memorySuggestion.audience_preference_memory || ""} />
          <Block label="不建议继续强化" value={memorySuggestion.negative_lessons || ""} />
        </div>
      </Card>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="rounded-lg border border-line bg-white p-4"><div className="text-xs text-muted">{label}</div><div className="mt-1 text-xl font-semibold">{value}</div></div>;
}

function Block({ label, value }: { label: string; value: string }) {
  return <div><div className="text-xs text-muted">{label}</div><div className="mt-1 rounded-md bg-surface p-3">{value || "暂无"}</div></div>;
}
