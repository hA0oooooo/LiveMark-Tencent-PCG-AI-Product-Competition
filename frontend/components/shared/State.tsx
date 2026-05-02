export function LoadingState({ text = "正在加载数据" }: { text?: string }) {
  return <div className="rounded-lg border border-line bg-white p-6 text-sm text-muted">{text}...</div>;
}

export function ErrorState({ message }: { message: string }) {
  return <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-sm text-red-700">{message}</div>;
}

export function EmptyState({ text }: { text: string }) {
  return <div className="rounded-lg border border-line bg-white p-6 text-sm text-muted">{text}</div>;
}
