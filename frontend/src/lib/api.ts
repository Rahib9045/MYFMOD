/**
 * api.ts — Single place that talks to the Flask backend.
 *
 * The auth token lives in localStorage and is attached to every request.
 * A 401 clears it and bounces the caller back to /login.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:5000";
const TOKEN_KEY = "auth_token";

export type Role = "recruiter" | "seeker";

export type User = {
  id: number;
  email: string;
  name: string;
  role: Role;
  company: string;
  has_cv: boolean;
  cv_filename: string;
  created_at: string | null;
};

export type Job = {
  id: number;
  title: string;
  company: string;
  location: string;
  employment_type: string;
  description: string;
  requirements: string;
  skills: string[];
  experience_level: string;
  salary_range: string;
  status: "open" | "closed";
  created_at: string | null;
  applicant_count?: number;
};

/** A job returned by the matcher, with its scores attached. */
export type JobMatch = Job & {
  match_score: number;
  relevance: number;
  fit: number;
  already_applied: boolean;
};

export type ApplicationStatus = "submitted" | "reviewed" | "shortlisted" | "rejected";

export type Application = {
  id: number;
  job_id: number;
  status: ApplicationStatus;
  match_score: number;
  cover_note: string;
  created_at: string | null;
  cv_text?: string;
  applicant?: { id: number; name: string; email: string };
  job?: { id: number; title: string; company: string; location: string; status: string };
};

export type JobInput = {
  title: string;
  company?: string;
  location?: string;
  employment_type?: string;
  description?: string;
  requirements?: string;
  skills?: string[] | string;
  experience_level?: string;
  salary_range?: string;
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

/** Where each role lands after signing in. */
export function homeFor(user: Pick<User, "role">) {
  return user.role === "recruiter" ? "/recruiter" : "/seeker";
}

// ── Auth ───────────────────────────────────────────────────────────────────
export async function register(input: {
  name: string;
  email: string;
  password: string;
  role: Role;
  company?: string;
}) {
  const data = await request<{ token: string; user: User }>("/auth/register", {
    method: "POST",
    body: JSON.stringify(input),
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
  return request<{ text: string; filename: string }>("/upload_pdf", {
    method: "POST",
    body: formData,
  });
}

// ── Jobs (recruiter writes, both roles read) ───────────────────────────────
export async function createJob(input: JobInput) {
  const data = await request<{ job: Job }>("/jobs", {
    method: "POST",
    body: JSON.stringify(input),
  });
  return data.job;
}

export async function myJobs() {
  const data = await request<{ jobs: Job[] }>("/jobs/mine");
  return data.jobs;
}

export async function browseJobs() {
  const data = await request<{ jobs: Job[] }>("/jobs");
  return data.jobs;
}

export async function updateJob(id: number, input: Partial<JobInput> & { status?: string }) {
  const data = await request<{ job: Job }>(`/jobs/${id}`, {
    method: "PUT",
    body: JSON.stringify(input),
  });
  return data.job;
}

export async function deleteJob(id: number) {
  return request<{ deleted: number }>(`/jobs/${id}`, { method: "DELETE" });
}

export async function jobApplications(jobId: number) {
  return request<{ job: Job; applications: Application[] }>(`/jobs/${jobId}/applications`);
}

export async function setApplicationStatus(id: number, status: ApplicationStatus) {
  const data = await request<{ application: Application }>(`/applications/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
  return data.application;
}

// ── Seeker: CV, matching, applying ─────────────────────────────────────────
export async function getCv() {
  return request<{ cv_text: string; cv_filename: string }>("/cv");
}

export async function saveCv(cv_text: string, cv_filename?: string) {
  const data = await request<{ saved: boolean; user: User }>("/cv", {
    method: "PUT",
    body: JSON.stringify({ cv_text, cv_filename }),
  });
  return data.user;
}

export async function matchJobs(input: { cv_text?: string; save_cv?: boolean; limit?: number } = {}) {
  return request<{ matches: JobMatch[]; total_open_jobs: number }>("/match", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function analyzeAgainstJob(jobId: number, cv_text?: string) {
  return request<{
    job_id: number;
    probability: number;
    decision: "SELECT" | "REJECT";
    advice: string;
    engine: string;
  }>(`/jobs/${jobId}/analyze`, {
    method: "POST",
    body: JSON.stringify({ cv_text }),
  });
}

export async function applyToJob(jobId: number, input: { cover_note?: string } = {}) {
  const data = await request<{ application: Application }>(`/jobs/${jobId}/apply`, {
    method: "POST",
    body: JSON.stringify(input),
  });
  return data.application;
}

export async function myApplications() {
  const data = await request<{ applications: Application[] }>("/applications/mine");
  return data.applications;
}
