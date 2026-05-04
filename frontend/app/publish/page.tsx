"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Trash2 } from "lucide-react";
import { deletePublishPlan, getDefaultAccount, getPublishPlans } from "@/lib/api";
import type { PublishPlan } from "@/lib/types";
import { targetMetricLabels } from "@/lib/constants";
import { formatDate } from "@/lib/format";
import { Card, CardTitle } from "@/components/ui/Card";
import { ErrorState, LoadingState, EmptyState } from "@/components/shared/State";

export default function PublishPage() {
  const [plans, setPlans] = useState<PublishPlan[]>([]);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadPlans();
  }, [status]);

  function loadPlans() {
    setLoading(true);
    getDefaultAccount()
      .then((account) => getPublishPlans({ account_id: account.id, status: status || undefined }))
      .then(setPlans)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }

  async function handleDelete(plan: PublishPlan) {
    if (!window.confirm(`确定删除发布计划「${plan.title}」吗？关联复盘和由复盘同步出的历史内容也会删除。`)) return;
    try {
      await deletePublishPlan(plan.id);
      setPlans((items) => items.filter((item) => item.id !== plan.id));
    } catch (err) {
      setError((err as Error).message);
    }
  }

  if (error) return <ErrorState message={error} />;

  return (
    <div className="page-grid">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">发布矩阵</h1>
          <p className="mt-1 text-sm text-muted">集中查看小红书发布建议、发布状态和复盘入口。</p>
        </div>
        <select value={status} onChange={(event) => setStatus(event.target.value)} className="rounded-md border border-line bg-white px-3 py-2 text-sm">
          <option value="">全部状态</option>
          <option value="draft">待发布</option>
          <option value="published">已发布</option>
          <option value="reviewed">已复盘</option>
        </select>
      </div>
      {loading ? <LoadingState text="正在加载发布矩阵" /> : plans.length === 0 ? <EmptyState text="暂无发布计划，请先完成素材分析并生成发布矩阵。" /> : (
        <div className="grid gap-4">
          {plans.map((plan) => (
            <Card key={plan.id} className="hover:border-accent">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <Link href={`/publish/${plan.id}`} className="min-w-0 flex-1">
                    <CardTitle>{plan.title}</CardTitle>
                    <p className="text-sm text-muted">{plan.caption}</p>
                  </Link>
                  <div className="flex items-center gap-2">
                    <div className="rounded-md bg-surface px-3 py-1 text-sm">{targetMetricLabels[plan.target_metric] || plan.target_metric}</div>
                    <button
                      type="button"
                      onClick={() => handleDelete(plan)}
                      className="rounded-md p-2 text-muted hover:bg-surface hover:text-brand"
                      aria-label="删除发布计划"
                      title="删除发布计划"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
                <Link href={`/publish/${plan.id}`} className="mt-3 grid gap-2 text-sm text-muted md:grid-cols-4">
                <div>状态：{plan.status}</div>
                <div>发布时间：{plan.recommended_publish_time}</div>
                <div>创建：{formatDate(plan.created_at)}</div>
                <div>封面文案：{plan.cover_text}</div>
              </Link>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
