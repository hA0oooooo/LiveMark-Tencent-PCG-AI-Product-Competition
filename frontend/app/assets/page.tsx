"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Plus } from "lucide-react";
import { getAssets, getDefaultAccount } from "@/lib/api";
import type { Asset } from "@/lib/types";
import { assetStatusLabels } from "@/lib/constants";
import { formatDate } from "@/lib/format";
import { Card, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { ErrorState, LoadingState, EmptyState } from "@/components/shared/State";

export default function AssetsPage() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getDefaultAccount()
      .then((account) => getAssets({ account_id: account.id }))
      .then(setAssets)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (error) return <ErrorState message={error} />;
  if (loading) return <LoadingState text="正在加载素材库" />;

  return (
    <div className="page-grid">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">素材库</h1>
          <p className="mt-1 text-sm text-muted">管理新上传的直拍素材、分析状态和发布矩阵状态。</p>
        </div>
        <Link href="/assets/upload"><Button><Plus size={16} />上传素材</Button></Link>
      </div>
      {assets.length === 0 ? <EmptyState text="还没有素材，请先上传一段直拍视频。" /> : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {assets.map((asset) => (
            <Link key={asset.id} href={`/assets/${asset.id}`}>
              <Card className="h-full hover:border-accent">
                <CardTitle>{asset.event_name}</CardTitle>
                <div className="grid gap-2 text-sm text-muted">
                  <div>目标人物：{asset.target_person || "未填写"}</div>
                  <div>上传时间：{formatDate(asset.upload_time)}</div>
                  <div>状态：{assetStatusLabels[asset.status]}</div>
                  <div>已分析：{["analyzed", "plan_generated", "reviewed"].includes(asset.status) ? "是" : "否"}</div>
                  <div>已生成发布矩阵：{["plan_generated", "reviewed"].includes(asset.status) ? "是" : "否"}</div>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
