"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { FormEvent, Suspense, useEffect, useState } from "react";
import { createPostResult, getDefaultAccount, getPublishPlans } from "@/lib/api";
import type { PostResult, PublishPlan } from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { Card, CardTitle } from "@/components/ui/Card";
import { Input, Label } from "@/components/ui/Field";
import { ErrorState, LoadingState } from "@/components/shared/State";

export default function ReviewPage() {
  return <Suspense fallback={<LoadingState text="正在加载复盘中心" />}><ReviewContent /></Suspense>;
}

function ReviewContent() {
  const search = useSearchParams();
  const [plans, setPlans] = useState<PublishPlan[]>([]);
  const [result, setResult] = useState<PostResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    getDefaultAccount()
      .then((account) => getPublishPlans({ account_id: account.id }))
      .then((items) => setPlans(items.filter((item) => item.status === "published" || item.status === "reviewed")))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    const form = new FormData(event.currentTarget);
    try {
      const created = await createPostResult({
        publish_plan_id: Number(form.get("publish_plan_id")),
        actual_title: String(form.get("actual_title") || ""),
        views: Number(form.get("views")),
        likes: Number(form.get("likes")),
        saves: Number(form.get("saves")),
        comments: Number(form.get("comments")),
        follows: form.get("follows") ? Number(form.get("follows")) : null
      });
      setResult(created);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  if (error) return <ErrorState message={error} />;
  if (loading) return <LoadingState text="正在加载可复盘发布计划" />;

  return (
    <div className="page-grid max-w-4xl">
      <div>
        <h1 className="text-2xl font-semibold">内容实验复盘</h1>
        <p className="mt-1 text-sm text-muted">手动录入发布后数据，系统基于账号基准生成下一轮增长建议。</p>
      </div>
      <Card>
        <CardTitle>提交复盘</CardTitle>
        <form onSubmit={submit} className="grid gap-4 md:grid-cols-2">
          <Label label="已发布计划">
            <select name="publish_plan_id" defaultValue={search.get("planId") || ""} className="w-full rounded-md border border-line bg-white px-3 py-2 text-sm" required>
              <option value="">请选择</option>
              {plans.map((plan) => <option key={plan.id} value={plan.id}>{plan.title}</option>)}
            </select>
          </Label>
          <Label label="实际标题"><Input name="actual_title" placeholder="可选" /></Label>
          <Label label="浏览"><Input name="views" type="number" required /></Label>
          <Label label="点赞"><Input name="likes" type="number" required /></Label>
          <Label label="收藏"><Input name="saves" type="number" required /></Label>
          <Label label="评论"><Input name="comments" type="number" required /></Label>
          <Label label="涨粉（可选）"><Input name="follows" type="number" /></Label>
          <div className="md:col-span-2"><Button disabled={submitting}>{submitting ? "正在生成复盘" : "提交内容实验复盘"}</Button></div>
        </form>
      </Card>
      {result && (
        <Card>
          <CardTitle>复盘已生成</CardTitle>
          <p className="text-sm text-muted">{result.next_action}</p>
          <Link href={`/review/${result.id}`}><Button className="mt-4" variant="secondary">查看复盘详情</Button></Link>
        </Card>
      )}
    </div>
  );
}
