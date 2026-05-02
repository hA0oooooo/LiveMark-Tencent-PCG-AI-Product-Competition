"use client";

import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getDashboardStats, getDefaultAccount } from "@/lib/api";
import type { DashboardStats } from "@/lib/types";
import { contentTypeLabels } from "@/lib/constants";
import { formatNumber } from "@/lib/format";
import { Card, CardTitle } from "@/components/ui/Card";
import { ErrorState, LoadingState } from "@/components/shared/State";

export default function DashboardPage() {
  const [data, setData] = useState<DashboardStats | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getDefaultAccount()
      .then((account) => getDashboardStats(account.id))
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  const formatChartValue = (value: unknown): string => {
    if (typeof value !== "number") return String(value ?? "");
    return Number.isInteger(value)
      ? formatNumber(value)
      : value.toLocaleString("zh-CN", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  };

  if (error) return <ErrorState message={error} />;
  if (!data) return <LoadingState text="正在加载账号增长主页" />;

  const metricCards = [
    ["粉丝量", formatNumber(data.account.follower_count)],
    ["当前发布笔记数", formatNumber(data.account.current_note_count)],
    ["当前获得点赞数", formatNumber(data.account.total_likes)],
    ["当前获得收藏数", formatNumber(data.account.total_saves)],
    ["素材数量", formatNumber(data.asset_count)],
    ["发布计划", formatNumber(data.publish_plan_count)]
  ];

  return (
    <div className="page-grid">
      <div>
        <h1 className="text-2xl font-semibold">账号增长主页</h1>
        <p className="mt-1 text-sm text-muted">围绕账号基准、资产状态和发布矩阵判断下一轮增长建议。</p>
      </div>
      <Card>
        <CardTitle>{data.account.name}</CardTitle>
        <div className="grid gap-2 text-sm text-muted md:grid-cols-3">
          <div>平台：{data.account.platform}</div>
          <div>垂类：{data.account.niche}</div>
          <div>表现最好的内容类型：{data.best_content_type ? contentTypeLabels[data.best_content_type] : "暂无"}</div>
        </div>
        <p className="mt-3 text-sm text-ink">{data.account.style_positioning}</p>
      </Card>
      <div className="grid gap-4 md:grid-cols-3 xl:grid-cols-5">
        {metricCards.map(([label, value]) => (
          <Card key={label}>
            <div className="text-sm text-muted">{label}</div>
            <div className="mt-2 text-2xl font-semibold">{value}</div>
          </Card>
        ))}
      </div>
      <div className="grid gap-4 xl:grid-cols-[1.5fr_1fr]">
        <Card>
          <CardTitle>内容类型表现图</CardTitle>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.content_type_performance.map((row) => ({ ...row, label: contentTypeLabels[row.content_type] || row.content_type }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="label" />
                <YAxis />
                <Tooltip formatter={(value) => formatChartValue(value)} />
                <Bar dataKey="avg_views" name="平均浏览" fill="#276f86" />
                <Bar dataKey="avg_saves" name="平均收藏" fill="#d83a56" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card>
          <CardTitle>下一轮增长建议</CardTitle>
          <div className="grid gap-3">
            {data.growth_insights.map((item) => (
              <div key={item} className="rounded-md bg-surface p-3 text-sm text-ink">
                {item}
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
