"use client";

import { FormEvent, useEffect, useState } from "react";
import { createHistoricalPost, getAccountBenchmark, getDefaultAccount, getHistoricalPosts, updateAccount } from "@/lib/api";
import type { Account, AccountBenchmark, HistoricalPost } from "@/lib/types";
import { contentTypeLabels } from "@/lib/constants";
import { formatNumber } from "@/lib/format";
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
      shares: Number(form.get("shares") || 0)
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
      <form onSubmit={saveAccount} className="grid gap-4 xl:grid-cols-[1fr_1.2fr]">
        <Card>
          <CardTitle>编辑账号画像</CardTitle>
          <div className="grid gap-3">
            <Label label="账号名"><Input name="name" defaultValue={account.name} /></Label>
            <Label label="账号垂类"><Input name="niche" defaultValue={account.niche} /></Label>
            <Label label="目标粉丝"><Textarea name="target_audience" defaultValue={account.target_audience} rows={3} /></Label>
            <Label label="账号风格定位"><Textarea name="style_positioning" defaultValue={account.style_positioning} rows={3} /></Label>
            <Label label="粉丝数"><Input name="follower_count" type="number" defaultValue={account.follower_count} /></Label>
            <Label label="当前发布笔记数"><Input name="current_note_count" type="number" defaultValue={account.current_note_count} /></Label>
            <Label label="当前获得点赞数"><Input name="total_likes" type="number" defaultValue={account.total_likes} /></Label>
            <Label label="当前获得收藏数"><Input name="total_saves" type="number" defaultValue={account.total_saves} /></Label>
          </div>
        </Card>
        <div className="grid gap-4">
          <Card>
            <CardTitle>账号基准数据</CardTitle>
            <div className="grid gap-3 md:grid-cols-2">
              <Metric label="粉丝数" value={formatNumber(account.follower_count)} />
              <Metric label="当前发布笔记数" value={formatNumber(account.current_note_count)} />
              <Metric label="当前获得点赞数" value={formatNumber(account.total_likes)} />
              <Metric label="当前获得收藏数" value={formatNumber(account.total_saves)} />
            </div>
          </Card>
          <Card>
            <CardTitle>账号长期记忆</CardTitle>
            <p className="mb-3 text-xs text-muted">由用户确认后维护；AI 复盘只给更新建议，不自动覆盖。未设置增长策略时，下一轮增长建议会根据历史内容和复盘数据生成可手动采纳的策略方向。</p>
            <div className="grid gap-3">
              <Label label="当前增长策略摘要"><Textarea name="strategy_summary" defaultValue={account.strategy_summary} rows={3} /></Label>
              <Label label="拍摄风格记忆"><Textarea name="shooting_style_memory" defaultValue={account.shooting_style_memory} rows={3} /></Label>
              <Label label="内容方向记忆"><Textarea name="content_direction_memory" defaultValue={account.content_direction_memory} rows={3} /></Label>
              <Label label="目标粉丝偏好记忆"><Textarea name="audience_preference_memory" defaultValue={account.audience_preference_memory} rows={3} /></Label>
              <Label label="不建议继续强化的内容"><Textarea name="negative_lessons" defaultValue={account.negative_lessons} rows={3} /></Label>
              <Button disabled={saving}>{saving ? "保存中" : "保存账号画像"}</Button>
            </div>
          </Card>
        </div>
      </form>
      <Card>
        <CardTitle>新增历史内容</CardTitle>
        <p className="mb-3 text-sm text-muted">这里只录入既往小红书笔记的数据指标，用来补充账号基准和内容类型表现；不上传历史视频。新视频素材请进入素材库上传，发布后的实际数据请在内容实验复盘中录入。</p>
        <form onSubmit={addPost} className="grid gap-3 md:grid-cols-6">
          <Input name="title" placeholder="标题" required />
          <select name="content_type" className="rounded-md border border-line px-3 py-2 text-sm">
            {Object.entries(contentTypeLabels).map(([key, label]) => <option key={key} value={key}>{label}</option>)}
          </select>
          <Input name="views" type="number" placeholder="浏览" required />
          <Input name="likes" type="number" placeholder="点赞" required />
          <Input name="saves" type="number" placeholder="收藏" required />
          <Input name="comments" type="number" placeholder="评论" required />
          <Input name="shares" type="number" placeholder="分享" />
          <Button className="md:col-span-1">新增</Button>
        </form>
      </Card>
      <Card>
        <CardTitle>历史内容表</CardTitle>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-muted">
              <tr><th className="py-2">标题</th><th>类型</th><th>浏览</th><th>点赞</th><th>收藏</th><th>评论</th><th>分享</th></tr>
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
                  <td>{formatNumber(post.shares || 0)}</td>
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
