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
  const normalized = /[zZ]|[+-]\d{2}:\d{2}$/.test(value) ? value : `${value}Z`;
  return new Date(normalized).toLocaleString("zh-CN", {
    hour12: false,
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  });
}

export function formatTimeRange(start: number, end: number): string {
  return `${start.toFixed(1)}s - ${end.toFixed(1)}s`;
}
