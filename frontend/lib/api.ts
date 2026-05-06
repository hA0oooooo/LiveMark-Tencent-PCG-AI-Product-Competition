import { API_BASE_URL } from "./constants";
import type {
  Account,
  AccountBenchmark,
  Asset,
  Clip,
  DashboardStats,
  HistoricalPost,
  PostResult,
  PublishPlan
} from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: init?.body instanceof FormData ? init.headers : { "Content-Type": "application/json", ...(init?.headers || {}) },
    cache: "no-store"
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(detail.detail || "请求失败");
  }
  return response.json() as Promise<T>;
}

export async function getDefaultAccount(): Promise<Account> {
  return request<Account>("/api/accounts/default");
}

export async function getAccount(accountId: number): Promise<Account> {
  return request<Account>(`/api/accounts/${accountId}`);
}

export async function updateAccount(accountId: number, payload: Partial<Account>): Promise<Account> {
  return request<Account>(`/api/accounts/${accountId}`, { method: "PUT", body: JSON.stringify(payload) });
}

export async function getAccountBenchmark(accountId: number): Promise<AccountBenchmark> {
  return request<AccountBenchmark>(`/api/accounts/${accountId}/benchmark`);
}

export async function getHistoricalPosts(accountId: number): Promise<HistoricalPost[]> {
  return request<HistoricalPost[]>(`/api/accounts/${accountId}/historical-posts`);
}

export async function createHistoricalPost(accountId: number, payload: Partial<HistoricalPost>): Promise<HistoricalPost> {
  return request<HistoricalPost>(`/api/accounts/${accountId}/historical-posts`, { method: "POST", body: JSON.stringify(payload) });
}

export async function deleteHistoricalPost(accountId: number, postId: number): Promise<{ message: string }> {
  return request<{ message: string }>(`/api/accounts/${accountId}/historical-posts/${postId}`, { method: "DELETE" });
}

export async function bulkCreateHistoricalPosts(accountId: number, payload: { posts: Partial<HistoricalPost>[] }): Promise<HistoricalPost[]> {
  return request<HistoricalPost[]>(`/api/accounts/${accountId}/historical-posts/bulk`, { method: "POST", body: JSON.stringify(payload) });
}

export async function getHistoricalPostStats(accountId: number) {
  return request(`/api/accounts/${accountId}/historical-posts/stats`);
}

export async function getDashboardStats(accountId: number): Promise<DashboardStats> {
  return request<DashboardStats>(`/api/dashboard/${accountId}`);
}

export async function uploadAsset(formData: FormData): Promise<{ asset: Asset; message: string }> {
  return request<{ asset: Asset; message: string }>("/api/assets/upload", { method: "POST", body: formData });
}

export async function getAssets(params?: { account_id?: number; status?: string }): Promise<Asset[]> {
  const search = new URLSearchParams();
  if (params?.account_id) search.set("account_id", String(params.account_id));
  if (params?.status) search.set("status", params.status);
  const suffix = search.toString() ? `?${search}` : "";
  return request<Asset[]>(`/api/assets${suffix}`);
}

export async function getAsset(assetId: number): Promise<Asset> {
  return request<Asset>(`/api/assets/${assetId}`);
}

export async function deleteAsset(assetId: number): Promise<{ message: string }> {
  return request<{ message: string }>(`/api/assets/${assetId}`, { method: "DELETE" });
}

export async function analyzeAsset(assetId: number): Promise<{ asset: Asset; message: string }> {
  return request<{ asset: Asset; message: string }>(`/api/assets/${assetId}/analyze`, { method: "POST" });
}

export async function getClipsByAsset(assetId: number) {
  return request(`/api/assets/${assetId}/clips`);
}

export async function getClip(clipId: number): Promise<Clip> {
  return request<Clip>(`/api/clips/${clipId}`);
}

export async function generatePublishMatrix(assetId: number): Promise<PublishPlan[]> {
  return request<PublishPlan[]>(`/api/assets/${assetId}/generate-publish-matrix`, { method: "POST" });
}

export async function getPublishPlans(params?: { account_id?: number; asset_id?: number; status?: string }): Promise<PublishPlan[]> {
  const search = new URLSearchParams();
  if (params?.account_id) search.set("account_id", String(params.account_id));
  if (params?.asset_id) search.set("asset_id", String(params.asset_id));
  if (params?.status) search.set("status", params.status);
  const suffix = search.toString() ? `?${search}` : "";
  return request<PublishPlan[]>(`/api/publish-plans${suffix}`);
}

export async function getPublishPlan(planId: number): Promise<PublishPlan> {
  return request<PublishPlan>(`/api/publish-plans/${planId}`);
}

export async function updatePublishPlan(planId: number, payload: Partial<PublishPlan>): Promise<PublishPlan> {
  return request<PublishPlan>(`/api/publish-plans/${planId}`, { method: "PUT", body: JSON.stringify(payload) });
}

export async function deletePublishPlan(planId: number): Promise<{ message: string }> {
  return request<{ message: string }>(`/api/publish-plans/${planId}`, { method: "DELETE" });
}

export async function createPostResult(payload: Partial<PostResult>): Promise<PostResult> {
  return request<PostResult>("/api/post-results", { method: "POST", body: JSON.stringify(payload) });
}

export async function getPostResult(postResultId: number): Promise<PostResult> {
  return request<PostResult>(`/api/post-results/${postResultId}`);
}

export async function getPostResultByPlan(planId: number): Promise<PostResult> {
  return request<PostResult>(`/api/publish-plans/${planId}/post-result`);
}

export async function integratePostResultMemory(postResultId: number): Promise<Account> {
  return request<Account>(`/api/post-results/${postResultId}/integrate-memory`, { method: "POST" });
}
