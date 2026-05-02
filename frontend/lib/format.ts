export function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined) return "暂无";
  return Math.round(value).toLocaleString("zh-CN");
}

export function formatRate(value: number | null | undefined): string {
  if (!value) return "暂无";
  return `${(value * 100).toFixed(1)}%`;
}

export function formatScore(value: number | null | undefined): string {
  if (value === null || value === undefined) return "0";
  return value.toFixed(1);
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "暂无";
  return new Date(value).toLocaleString("zh-CN", { hour12: false });
}

export function formatTimeRange(start: number, end: number): string {
  return `${start.toFixed(1)}s - ${end.toFixed(1)}s`;
}
