"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { analyzeAsset, generatePublishMatrix, getAsset } from "@/lib/api";
import type { Asset } from "@/lib/types";
import { assetStatusLabels } from "@/lib/constants";
import { formatDate, formatScore, formatTimeRange } from "@/lib/format";
import { mediaUrl } from "@/lib/utils";
import { Button } from "@/components/ui/Button";
import { Card, CardTitle } from "@/components/ui/Card";
import { ErrorState, LoadingState } from "@/components/shared/State";

export default function AssetDetailPage() {
  const { assetId } = useParams<{ assetId: string }>();
  const router = useRouter();
  const [asset, setAsset] = useState<Asset | null>(null);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");

  const load = () => getAsset(Number(assetId)).then(setAsset).catch((err) => setError(err.message));
  useEffect(() => { load(); }, [assetId]);

  async function runAnalyze() {
    setBusy("正在进行 AI 分析，视频抽帧可能需要一些时间");
    setError("");
    try {
      const result = await analyzeAsset(Number(assetId));
      setAsset(result.asset);
      router.push(`/assets/${assetId}/analysis`);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy("");
    }
  }

  async function runMatrix() {
    setBusy("正在生成小红书发布矩阵");
    setError("");
    try {
      await generatePublishMatrix(Number(assetId));
      await load();
      router.push("/publish");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy("");
    }
  }

  if (error) return <ErrorState message={error} />;
  if (!asset) return <LoadingState text="正在加载素材详情" />;

  return (
    <div className="page-grid">
      <div>
        <h1 className="text-2xl font-semibold">{asset.event_name}</h1>
        <p className="mt-1 text-sm text-muted">状态：{assetStatusLabels[asset.status]} · 上传时间：{formatDate(asset.upload_time)}</p>
      </div>
      {busy && <LoadingState text={busy} />}
      <div className="grid gap-4 xl:grid-cols-[1.4fr_1fr]">
        <Card>
          <CardTitle>视频预览</CardTitle>
          <video src={mediaUrl(asset.video_path)} controls className="aspect-video w-full rounded-md bg-black" />
        </Card>
        <Card>
          <CardTitle>素材信息</CardTitle>
          <div className="grid gap-2 text-sm text-muted">
            <div>场景类型：{asset.scene_type || "未填写"}</div>
            <div>目标人物：{asset.target_person || "未填写"}</div>
            <div>素材背景：{asset.context_note || "未填写"}</div>
            <div>时长：{asset.duration.toFixed(1)} 秒</div>
            <div>摘要：{asset.summary || "暂无"}</div>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {asset.status === "uploaded" && <Button onClick={runAnalyze}>开始 AI 分析</Button>}
            {asset.status === "analyzed" && <Button onClick={runMatrix}>生成小红书发布矩阵</Button>}
            {asset.status === "plan_generated" && <Link href="/publish"><Button>查看发布矩阵</Button></Link>}
            {["analyzed", "plan_generated", "reviewed"].includes(asset.status) && <Link href={`/assets/${asset.id}/analysis`}><Button variant="secondary">查看分析结果</Button></Link>}
          </div>
        </Card>
      </div>
      <div className="grid gap-4 xl:grid-cols-3">
        <Card><CardTitle>抽帧摘要</CardTitle><p className="text-sm text-muted">共 {asset.frames?.length || 0} 张帧，关键帧 {asset.frames?.filter((f) => f.is_selected).length || 0} 张。</p></Card>
        <Card><CardTitle>候选片段摘要</CardTitle>{asset.clips?.map((clip) => <p key={clip.id} className="text-sm text-muted">{formatTimeRange(clip.start_time, clip.end_time)} · 涨粉机会评分 {formatScore(clip.growth_score)}</p>)}</Card>
        <Card><CardTitle>发布计划摘要</CardTitle><p className="text-sm text-muted">已生成 {asset.publish_plans?.length || 0} 条小红书发布建议。</p></Card>
      </div>
    </div>
  );
}
