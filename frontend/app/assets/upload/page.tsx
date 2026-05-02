"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getDefaultAccount, uploadAsset } from "@/lib/api";
import type { Account } from "@/lib/types";
import { Card, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input, Label, Textarea } from "@/components/ui/Field";
import { ErrorState, LoadingState } from "@/components/shared/State";

export default function UploadAssetPage() {
  const router = useRouter();
  const [account, setAccount] = useState<Account | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getDefaultAccount().then(setAccount).catch((err) => setError(err.message));
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!account) return;
    setLoading(true);
    setError("");
    const form = new FormData(event.currentTarget);
    form.set("account_id", String(account.id));
    try {
      const result = await uploadAsset(form);
      router.push(`/assets/${result.asset.id}`);
    } catch (err) {
      setError((err as Error).message);
      setLoading(false);
    }
  }

  if (error) return <ErrorState message={error} />;
  if (!account) return <LoadingState text="正在读取默认账号" />;

  return (
    <div className="page-grid max-w-3xl">
      <div>
        <h1 className="text-2xl font-semibold">上传素材</h1>
        <p className="mt-1 text-sm text-muted">上传新直拍视频，系统只保存本地路径并用于抽帧分析。</p>
      </div>
      <Card>
        <CardTitle>素材信息</CardTitle>
        <form onSubmit={submit} className="grid gap-4">
          <input type="hidden" name="account_id" value={account.id} />
          <Label label="视频文件"><Input name="file" type="file" accept="video/*" required /></Label>
          <Label label="活动名称"><Input name="event_name" placeholder="例如：春季赛线下现场" required /></Label>
          <Label label="场景类型"><Input name="scene_type" placeholder="例如：赛后互动" /></Label>
          <Label label="目标人物"><Input name="target_person" placeholder="例如：选手名 / 队伍名" /></Label>
          <Label label="素材背景说明"><Textarea name="context_note" rows={4} placeholder="补充活动背景、人物身份、现场发生了什么、你希望重点分析的看点。AI 不联网识别人物，会优先参考这里。" /></Label>
          <Button disabled={loading}>{loading ? "上传中" : "上传素材"}</Button>
        </form>
      </Card>
    </div>
  );
}
