"use client";

import { FormEvent, useEffect, useState } from "react";
import { createHistoricalPost, getAccountBenchmark, getDefaultAccount, getHistoricalPosts, updateAccount } from "@/lib/api";
import type { Account, AccountBenchmark, HistoricalPost } from "@/lib/types";
import { contentTypeLabels } from "@/lib/constants";
import { formatNumber, formatRate } from "@/lib/format";
import { Card, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input, Label, Textarea } from "@/components/ui/Field";
import { ErrorState, LoadingState } from "@/components/shared/State";

export default function AccountPage() {
  const [account, setAccount] = useState<Account | null>(null);
  const [benchmark, setBenchmark] = useState<AccountBenchmark | null>(null);
  const [posts, setPosts] = useState<HistoricalPost[]>([]);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const load = () =>
    getDefaultAccount()
      .then(async (acc) => {
        setAccount(acc);
        setBenchmark(await getAccountBenchmark(acc.id));
        setPosts(await getHistoricalPosts(acc.id));
      })
      .catch((err) => setError(err.message));

  useEffect(() => {
    load();
  }, []);

  async function saveAccount(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!account) return;
    setSaving(true);
    const form = new FormData(event.currentTarget);
    try {
      const next = await updateAccount(account.id, Object.fromEntries(form.entries()) as Partial<Account>);
      setAccount(next);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSaving(false);
    }
  }

  async function addPost(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!account) return;
    const form = new FormData(event.currentTarget);
    await createHistoricalPost(account.id, {
      title: String(form.get("title")),
      content_type: String(form.get("content_type")),
      views: Number(form.get("views")),
      likes: Number(form.get("likes")),
      saves: Number(form.get("saves")),
      comments: Number(form.get("comments")),
      follows: Number(form.get("follows") || 0),
      creator_note: String(form.get("creator_note") || "")
    });
    event.currentTarget.reset();
    await load();
  }

  if (error) return <ErrorState message={error} />;
  if (!account || !benchmark) return <LoadingState text="正在加载账号画像" />;

  return (
    <div className="page-grid">
      <div>
        <h1 className="text-2xl font-semibold">账号画像与历史数据</h1>
        <p className="mt-1 text-sm text-muted">历史内容只用于建立账号基准，不用于训练模型。</p>
      </div>
      <div className="grid gap-4 xl:grid-cols-[1fr_1.2fr]">
        <Card>
          <CardTitle>编辑账号画像</CardTitle>
          <form onSubmit={saveAccount} className="grid gap-3">
            <Label label="账号名"><Input name="name" defaultValue={account.name} /></Label>
            <Label label="账号垂类"><Input name="niche" defaultValue={account.niche} /></Label>
            <Label label="目标粉丝"><Textarea name="target_audience" defaultValue={account.target_audience} rows={3} /></Label>
            <Label label="账号风格定位"><Textarea name="style_positioning" defaultValue={account.style_positioning} rows={3} /></Label>
            <Label label="粉丝数"><Input name="follower_count" type="number" defaultValue={account.follower_count} /></Label>
            <Button disabled={saving}>{saving ? "保存中" : "保存账号画像"}</Button>
          </form>
        </Card>
        <Card>
          <CardTitle>账号基准数据</CardTitle>
          <div className="grid gap-3 md:grid-cols-3">
            <Metric label="平均浏览" value={formatNumber(benchmark.avg_views)} />
            <Metric label="平均点赞率" value={formatRate(benchmark.avg_like_rate)} />
            <Metric label="平均收藏率" value={formatRate(benchmark.avg_save_rate)} />
            <Metric label="平均评论率" value={formatRate(benchmark.avg_comment_rate)} />
            <Metric label="平均转粉率" value={benchmark.avg_follows ? formatRate(benchmark.avg_follow_rate) : "暂无"} />
            <Metric label="历史内容" value={formatNumber(benchmark.historical_post_count)} />
          </div>
        </Card>
      </div>
      <Card>
        <CardTitle>新增历史内容</CardTitle>
        <form onSubmit={addPost} className="grid gap-3 md:grid-cols-6">
          <Input name="title" placeholder="标题" required />
          <select name="content_type" className="rounded-md border border-line px-3 py-2 text-sm">
            {Object.entries(contentTypeLabels).map(([key, label]) => <option key={key} value={key}>{label}</option>)}
          </select>
          <Input name="views" type="number" placeholder="浏览" required />
          <Input name="likes" type="number" placeholder="点赞" required />
          <Input name="saves" type="number" placeholder="收藏" required />
          <Input name="comments" type="number" placeholder="评论" required />
          <Input name="follows" type="number" placeholder="涨粉，可选" />
          <Input name="creator_note" placeholder="创作者判断" className="md:col-span-4" />
          <Button className="md:col-span-1">新增</Button>
        </form>
      </Card>
      <Card>
        <CardTitle>历史内容表</CardTitle>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-muted">
              <tr><th className="py-2">标题</th><th>类型</th><th>浏览</th><th>点赞</th><th>收藏</th><th>评论</th><th>涨粉</th><th>判断</th></tr>
            </thead>
            <tbody>
              {posts.map((post) => (
                <tr key={post.id} className="border-t border-line">
                  <td className="py-2">{post.title}</td>
                  <td>{contentTypeLabels[post.content_type]}</td>
                  <td>{formatNumber(post.views)}</td>
                  <td>{formatNumber(post.likes)}</td>
                  <td>{formatNumber(post.saves)}</td>
                  <td>{formatNumber(post.comments)}</td>
                  <td>{post.follows ? formatNumber(post.follows) : "暂无"}</td>
                  <td>{post.creator_note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="rounded-md bg-surface p-3"><div className="text-xs text-muted">{label}</div><div className="mt-1 text-xl font-semibold">{value}</div></div>;
}
