import { API_BASE_URL } from "./constants";

export function mediaUrl(path?: string): string {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  const normalized = path.replaceAll("\\", "/");
  const upload = normalized.match(/uploads\/(.+)$/);
  const frame = normalized.match(/frames\/(.+)$/);
  const clip = normalized.match(/clips\/(.+)$/);
  if (upload) return `${API_BASE_URL}/uploads/${upload[1]}`;
  if (frame) return `${API_BASE_URL}/frames/${frame[1]}`;
  if (clip) return `${API_BASE_URL}/clips/${clip[1]}`;
  return `${API_BASE_URL}/${normalized.replace(/^\/+/, "")}`;
}

export function parseJsonText<T>(text: string, fallback: T): T {
  try {
    return JSON.parse(text) as T;
  } catch {
    return fallback;
  }
}
