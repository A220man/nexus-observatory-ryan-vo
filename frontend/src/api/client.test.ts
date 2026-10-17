/**
 * Tests for the typed API client.
 *
 * The client is constructed with an injected ``fetch`` so no real network
 * calls are made.
 */
import { describe, it, expect, vi } from "vitest";
import { createClient, ApiError } from "./client";

type MockResponse = {
  ok: boolean;
  status: number;
  statusText?: string;
  body: unknown;
  headers?: Record<string, string>;
};

/** Build a mock fetch that returns *response*. */
function makeMockFetch(response: MockResponse) {
  return vi.fn(async (_url: string, _init?: RequestInit) => ({
    ok: response.ok,
    status: response.status,
    statusText: response.statusText ?? "",
    headers: new Headers(response.headers ?? { "Content-Type": "application/json" }),
    json: async () => response.body,
  }));
}

describe("createClient health()", () => {
  it("calls /health and returns the parsed body", async () => {
    const fetch = makeMockFetch({
      ok: true,
      status: 200,
      body: { status: "ok", app: "nexus-observatory", version: "1.0.0" },
    });
    const client = createClient({ fetch: fetch as unknown as typeof globalThis.fetch });

    const result = await client.health();
    expect(result.status).toBe("ok");
    expect(result.app).toBe("nexus-observatory");
    expect(fetch).toHaveBeenCalledWith("/health", expect.objectContaining({}));
  });
});

describe("createClient parseLink()", () => {
  const mockRecord = {
    id: 1,
    input_url: "https://pan.baidu.com/s/1abc",
    provider: "baidu",
    resource_id: "1abc",
    password: "",
    direct_link: "",
    strategy: "test",
    status: "parsed",
    confidence: 0.9,
    error: null,
    created_at: "2026-01-01T00:00:00Z",
  };

  it("POSTs the URL and returns the record", async () => {
    const fetch = makeMockFetch({ ok: true, status: 200, body: mockRecord });
    const client = createClient({ fetch: fetch as unknown as typeof globalThis.fetch });

    const record = await client.parseLink("https://pan.baidu.com/s/1abc");
    expect(record.provider).toBe("baidu");
    expect(record.status).toBe("parsed");
    expect(fetch).toHaveBeenCalledTimes(1);
    const [url, init] = fetch.mock.calls[0];
    expect(url).toBe("/api/v1/links");
    expect(init?.method).toBe("POST");
    expect(JSON.parse(init?.body as string)).toEqual({
      url: "https://pan.baidu.com/s/1abc",
    });
  });
});

describe("createClient listLinks()", () => {
  it("builds query string with pagination params", async () => {
    const fetch = makeMockFetch({
      ok: true,
      status: 200,
      body: { items: [], total: 0, page: 2, limit: 10 },
    });
    const client = createClient({ fetch: fetch as unknown as typeof globalThis.fetch });

    await client.listLinks(2, 10, "baidu", "parsed");
    const [url] = fetch.mock.calls[0];
    expect(url).toContain("page=2");
    expect(url).toContain("limit=10");
    expect(url).toContain("provider=baidu");
    expect(url).toContain("status=parsed");
  });
});

describe("createClient getStatuses()", () => {
  it("returns the list of status strings", async () => {
    const fetch = makeMockFetch({
      ok: true,
      status: 200,
      body: ["parsed", "needs_password", "unsupported", "error"],
    });
    const client = createClient({ fetch: fetch as unknown as typeof globalThis.fetch });

    const statuses = await client.getStatuses();
    expect(statuses).toEqual(["parsed", "needs_password", "unsupported", "error"]);
  });
});

describe("createClient getProviders()", () => {
  it("returns provider list", async () => {
    const fetch = makeMockFetch({
      ok: true,
      status: 200,
      body: [
        {
          key: "baidu",
          name: "Baidu Cloud",
          domains: ["pan.baidu.com"],
          password_param: "pwd",
          strategy: "test",
        },
      ],
    });
    const client = createClient({ fetch: fetch as unknown as typeof globalThis.fetch });

    const providers = await client.getProviders();
    expect(providers).toHaveLength(1);
    expect(providers[0].key).toBe("baidu");
  });
});

describe("createClient classify()", () => {
  it("POSTs the URL and returns provider + confidence", async () => {
    const fetch = makeMockFetch({
      ok: true,
      status: 200,
      body: {
        provider: "baidu",
        confidence: 0.95,
        probabilities: { baidu: 0.95 },
      },
    });
    const client = createClient({ fetch: fetch as unknown as typeof globalThis.fetch });

    const result = await client.classify("https://pan.baidu.com/s/1abc");
    expect(result.provider).toBe("baidu");
    expect(result.confidence).toBe(0.95);
  });
});

describe("createClient error handling", () => {
  it("throws ApiError on non-ok response", async () => {
    const fetch = makeMockFetch({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
      body: { detail: "boom" },
    });
    const client = createClient({ fetch: fetch as unknown as typeof globalThis.fetch });

    await expect(client.health()).rejects.toThrow(ApiError);
  });
});