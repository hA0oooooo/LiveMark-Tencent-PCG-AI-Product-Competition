"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Plus, Trash2 } from "lucide-react";
import { deleteAsset, getAssets, getDefaultAccount } from "@/lib/api";
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
    loadAssets();
  }, []);

  function loadAssets() {
    setLoading(true);
    getDefaultAccount()
      .then((account) => getAssets({ account_id: account.id }))
      .then(setAssets)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }

  async function handleDelete(asset: Asset) {
    if (!window.confirm(`确定删除素材「${asset.event_name}」吗？关联的抽帧、候选片段、发布计划和复盘也会删除。`)) return;
    try {
      await deleteAsset(asset.id);
      setAssets((items) => items.filter((item) => item.id !== asset.id));
      window.dispatchEvent(new Event("livemark-data-changed"));
    } catch (err) {
      setError((err as Error).message);
    }
  }

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
            <Card key={asset.id} className="h-full hover:border-accent">
              <div className="flex items-start justify-between gap-3">
                <Link href={`/assets/${asset.id}`} className="min-w-0 flex-1">
                  <CardTitle>{asset.event_name}</CardTitle>
                </Link>
                <button
                  type="button"
                  onClick={() => handleDelete(asset)}
                  className="rounded-md p-2 text-muted hover:bg-surface hover:text-brand"
                  aria-label="删除素材"
                  title="删除素材"
                >
                  <Trash2 size={16} />
                </button>
              </div>
              <Link href={`/assets/${asset.id}`} className="block">
                <div className="grid gap-2 text-sm text-muted">
                  <div>目标人物：{asset.target_person || "未填写"}</div>
                  <div>上传时间：{formatDate(asset.upload_time)}</div>
                  <div>状态：{assetStatusLabels[asset.status]}</div>
                  <div>已分析：{["analyzed", "plan_generated", "reviewed"].includes(asset.status) ? "是" : "否"}</div>
                  <div>已生成发布矩阵：{["plan_generated", "reviewed"].includes(asset.status) ? "是" : "否"}</div>
                </div>
              </Link>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
