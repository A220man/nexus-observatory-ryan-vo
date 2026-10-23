/**
 * Typed API client for the Nexus Observatory backend.
 *
 * Uses the built-in `fetch` API — no external HTTP dependency required.
 * All endpoints live under `/api/v1` (plus `/health`).
 */

// ── type aliases ──────────────────────────────────────────────

export type ParseStatus = "parsed" | "needs_password" | "unsupported" | "error";

export interface LinkRecord {
  id: number;
  input_url: string;
  provider: string;
  resource_id: string;
  password: string;
  direct_link: string;
  strategy: string;
  status: ParseStatus;
  confidence: number;
  error: string | null;
  created_at: string;
}

export interface LinkListResponse {
  items: LinkRecord[];
  total: number;
  page: number;
  limit: number;
}

export interface ParseRequest {
  url: string;
}

export interface ParseResult {
  record: LinkRecord | null;
  classification: { provider: string; confidence: number } | null;
  error: string | null;
}

export interface ClassifyResponse {
  provider: string;
  confidence: number;
  probabilities: Record<string, number>;
}

export interface ClassifyRequest {
  url: string;
}

export interface ProviderInfo {
  key: string;
  name: string;
  domains: string[];
  password_param: string | null;
  strategy: string;
}

export interface EvaluateResponse {
  accuracy: number;
  per_class: Record<string, { precision: number; recall: number; f1: number; support: number }>;
  n_samples: number;
  n_classes: number;
  train_size: number;
  test_size: number;
  confusion_matrix: number[][];
}

export interface HealthResponse {
  status: string;
  app: string;
  version: string;
}

// ── low-level transport ───────────────────────────────────────

const DEFAULT_BASE_URL = "";

export class ApiError extends Error {
  constructor(message: string, public status: number, public body: unknown) {
    super(message);
    this.name = "ApiError";
  }
}

export interface ClientOptions {
  baseUrl?: string;
  fetch?: typeof globalThis.fetch;
}

/**
 * Create a typed API client bound to *baseUrl*.
 *
 * In the browser, the Vite dev server proxies `/api` and `/health` to the
 * backend, so `baseUrl` can stay empty.  In production, set `baseUrl` to the
 * full backend origin (or leave empty for same-origin deploys).
 */
export function createClient(opts: ClientOptions = {}) {
  const baseUrl = opts.baseUrl ?? DEFAULT_BASE_URL;
  const fetchImpl = opts.fetch ?? globalThis.fetch;

  async function request<T>(path: string, init?: RequestInit): Promise<T> {
    const url = `${baseUrl}${path}`;
    const resp = await fetchImpl(url, {
      headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
      ...init,
    });
    if (!resp.ok) {
      let body: unknown = undefined;
      try {
        body = await resp.json();
      } catch {
        body = await resp.text();
      }
      throw new ApiError(
        `API ${resp.status}: ${resp.statusText || "error"}`,
        resp.status,
        body,
      );
    }
    const contentLength = resp.headers.get("Content-Length");
    if (resp.status === 204 || contentLength === "0") {
      return undefined as T;
    }
    return resp.json() as Promise<T>;
  }

  return {
    // ── health ──
    health: () => request<HealthResponse>("/health"),

    // ── links ──
    parseLink: (url: string) => request<LinkRecord>("/api/v1/links", {
      method: "POST",
      body: JSON.stringify({ url } satisfies ParseRequest),
    }),

    listLinks: (page = 1, limit = 20, provider?: string, status?: string) => {
      const params = new URLSearchParams({ page: String(page), limit: String(limit) });
      if (provider) params.append("provider", provider);
      if (status) params.append("status", status);
      return request<LinkListResponse>(`/api/v1/links?${params.toString()}`);
    },

    getLink: (id: number) => request<LinkRecord>(`/api/v1/links/${id}`),

    exportLinks: (format: "json" | "csv" = "json") =>
      fetchImpl(`${baseUrl}/api/v1/links/export?format=${format}`).then((resp) => {
        if (!resp.ok) {
          throw new ApiError(
            `API ${resp.status}: ${resp.statusText || "error"}`,
            resp.status,
            undefined,
          );
        }
        return resp.blob();
      }),

    // ── statuses ──
    getStatuses: () => request<ParseStatus[]>("/api/v1/statuses"),

    // ── classifier ──
    classify: (url: string) =>
      request<ClassifyResponse>("/api/v1/classify", {
        method: "POST",
        body: JSON.stringify({ url } satisfies ClassifyRequest),
      }),

    getProviders: () => request<ProviderInfo[]>("/api/v1/providers"),

    evaluate: () => request<EvaluateResponse>("/api/v1/evaluate", { method: "POST" }),
  };
}

/** Default client instance for use in the app. */
export const api = createClient();