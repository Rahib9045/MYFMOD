/**
 * api.ts — Single place that talks to the Flask backend.
 *
 * The auth token lives in localStorage and is attached to every request.
 * A 401 clears it and bounces the caller back to /login.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:5000";
const TOKEN_KEY = "auth_token";

export type User = {
  id: number;
  email: string;
  name: string;
  created_at: string | null;
};

export type Portfolio = {
  id: number;
  title: string;
  resume: string;
  transcript: string;
  job_description: string;
  created_at: string | null;
  updated_at: string | null;
};

export type Analysis = {
  id: number;
  portfolio_id: number | null;
  probability: number;
  decision: "SELECT" | "REJECT";
  advice: string;
  engine: string;
  created_at: string | null;
  job_preview?: string;
};

export type PredictResult = {
  analysis_id: number;
  probability: number;
  decision: "SELECT" | "REJECT";
  advice: string;
  engine: string;
  message: string;
};

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const isFormData = options.body instanceof FormData;

  const headers: Record<string, string> = {
    ...(isFormData ? {} : { "Content-Type": "application/json" }),
    ...((options.headers as Record<string, string>) ?? {}),
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, { ...options, headers });
  } catch {
    throw new ApiError(`Cannot reach the API at ${API_URL}. Is the backend running?`, 0);
  }

  if (response.status === 401) {
    clearToken();
    if (typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
      window.location.href = "/login";
    }
    throw new ApiError("Your session expired. Please sign in again.", 401);
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new ApiError(data.error ?? `Request failed (${response.status})`, response.status);
  }
  return data as T;
}

// ── Auth ───────────────────────────────────────────────────────────────────
export async function register(name: string, email: string, password: string) {
  const data = await request<{ token: string; user: User }>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ name, email, password }),
  });
  setToken(data.token);
  return data.user;
}

export async function login(email: string, password: string) {
  const data = await request<{ token: string; user: User }>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setToken(data.token);
  return data.user;
}

export async function me() {
  const data = await request<{ user: User }>("/auth/me");
  return data.user;
}

export function logout() {
  clearToken();
}

// ── Portfolios ─────────────────────────────────────────────────────────────
export async function listPortfolios() {
  const data = await request<{ portfolios: Portfolio[] }>("/portfolios");
  return data.portfolios;
}

export async function createPortfolio(input: {
  title: string;
  resume: string;
  transcript: string;
  job_description: string;
}) {
  const data = await request<{ portfolio: Portfolio }>("/portfolios", {
    method: "POST",
    body: JSON.stringify(input),
  });
  return data.portfolio;
}

export async function deletePortfolio(id: number) {
  return request<{ deleted: number }>(`/portfolios/${id}`, { method: "DELETE" });
}

// ── Analyses ───────────────────────────────────────────────────────────────
export async function listAnalyses(limit = 20) {
  const data = await request<{ analyses: Analysis[] }>(`/analyses?limit=${limit}`);
  return data.analyses;
}

export async function getAnalysis(id: number) {
  const data = await request<{ analysis: Analysis & { resume: string; transcript: string; job_description: string } }>(
    `/analyses/${id}`
  );
  return data.analysis;
}

export async function deleteAnalysis(id: number) {
  return request<{ deleted: number }>(`/analyses/${id}`, { method: "DELETE" });
}

// ── Prediction ─────────────────────────────────────────────────────────────
export async function predict(input: {
  resume: string;
  transcript: string;
  job_description: string;
  portfolio_id?: number | null;
}) {
  return request<PredictResult>("/predict", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function uploadPdf(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const data = await request<{ text: string }>("/upload_pdf", {
    method: "POST",
    body: formData,
  });
  return data.text;
}
