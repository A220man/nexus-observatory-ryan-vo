
/**
 * Tests for the LinkList component.
 */
import { describe, it, expect, vi, beforeEach, waitFor } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import LinkList from "./LinkList";
import { LinkRecord, LinkListResponse, ParseStatus, api } from "../api/client";

vi.mock("../api/client", () => ({
  api: {
    listLinks: vi.fn(),
    exportLinks: vi.fn(),
  },
  ApiError: class ApiError extends Error {
    status: number;
    body: unknown;
    constructor(message: string, status: number, body: unknown) {
      super(message);
      this.name = "ApiError";
      this.status = status;
      this.body = body;
    }
  },
}));

import { api } from "../api/client";
const listLinksMock = vi.mocked(api.listLinks);
const exportLinksMock = vi.mocked(api.exportLinks);

const mockRecords: LinkRecord[] = [
  {
    id: 1,
    input_url: "https://pan.baidu.com/s/1abc",
    provider: "baidu",
    resource_id: "1abc",
    password: "1234",
    direct_link: "",
    strategy: "redirect",
    status: "parsed",
    confidence: 0.95,
    error: null,
    created_at: "2026-01-01T00:00:00Z",
  },
  {
    id: 2,
    input_url: "https://aliyuncloud.com/s/2def",
    provider: "aliyun",
    resource_id: "2def",
    password: "",
    direct_link: "",
    strategy: "direct",
    status: "parsed",
    confidence: 0.88,
    error: null,
    created_at: "2026-01-02T00:00:00Z",
  },
  {
    id: 3,
    input_url: "https://pan.xunlei.com/s/3ghi",
    provider: "xunlei",
    resource_id: "3ghi",
    password: "5678",
    direct_link: "",
    strategy: "redirect",
    status: "needs_password",
    confidence: 0.72,
    error: null,
    created_at: "2026-01-03T00:00:00Z",
  },
];

const mockResponse: LinkListResponse = {
  items: mockRecords,
  total: 3,
  page: 1,
  limit: 20,
};

describe("<LinkList>", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    listLinksMock.mockResolvedValue(mockResponse);
    exportLinksMock.mockResolvedValue(new Blob(["test"], { type: "application/json" }));
    
    // Mock URL.createObjectURL and revokeObjectURL for jsdom
    vi.stubGlobal("URL", {
      ...global.URL,
      createObjectURL: vi.fn().mockReturnValue("blob:mock"),
      revokeObjectURL: vi.fn(),
    });
  });

  it("renders loading state initially", async () => {
    render(<LinkList />);
    await waitFor(() => {
      expect(screen.getByText("Loading…")).toBeInTheDocument();
    });
  });

  it("renders catalog with records after loading", async () => {
    render(<LinkList />);
    await waitFor(() => {
      expect(screen.getByText("Catalog")).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(screen.getByText("baidu")).toBeInTheDocument();
      expect(screen.getByText("aliyun")).toBeInTheDocument();
      expect(screen.getByText("xunlei")).toBeInTheDocument();
    });
  });

  it("shows empty state when no records", async () => {
    listLinksMock.mockResolvedValueOnce({ items: [], total: 0, page: 1, limit: 20 });
    render(<LinkList />);
    await waitFor(() => {
      expect(screen.getByText("No records yet. Parse a share URL to get started.")).toBeInTheDocument();
    });
  });

  it("shows error state when API fails", async () => {
    listLinksMock.mockRejectedValueOnce(new Error("Network error"));
    render(<LinkList />);
    await waitFor(() => {
      expect(screen.getByRole("alert")).toBeInTheDocument();
      expect(screen.getByText("Error: Network error")).toBeInTheDocument();
    });
  });

  it("renders provider filter input", async () => {
    render(<LinkList />);
    await waitFor(() => {
      expect(screen.getByPlaceholderText("Filter by provider key…")).toBeInTheDocument();
    });
  });

  it("renders status filter select with all options", async () => {
    render(<LinkList />);
    await waitFor(() => {
      const select = screen.getByRole("combobox");
      expect(select).toBeInTheDocument();
      expect(screen.getByText("All")).toBeInTheDocument();
      expect(screen.getByText("parsed")).toBeInTheDocument();
      expect(screen.getByText("needs_password")).toBeInTheDocument();
      expect(screen.getByText("unsupported")).toBeInTheDocument();
      expect(screen.getByText("error")).toBeInTheDocument();
    });
  });

  it("renders export buttons", async () => {
    render(<LinkList />);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Export JSON" })).toBeInTheDocument();
      expect(screen.getByRole("button", { name: "Export CSV" })).toBeInTheDocument();
    });
  });

  it("calls exportLinks on JSON export click", async () => {
    render(<LinkList />);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Export JSON" })).toBeInTheDocument();
    });
    await userEvent.click(screen.getByRole("button", { name: "Export JSON" }));
    await waitFor(() => {
      expect(exportLinksMock).toHaveBeenCalledWith("json", undefined, undefined);
    });
  });

  it("calls exportLinks on CSV export click", async () => {
    render(<LinkList />);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Export CSV" })).toBeInTheDocument();
    });
    await userEvent.click(screen.getByRole("button", { name: "Export CSV" }));
    await waitFor(() => {
      expect(exportLinksMock).toHaveBeenCalledWith("csv", undefined, undefined);
    });
  });

  it("calls exportLinks with current provider filter", async () => {
    render(<LinkList />);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Export JSON" })).toBeInTheDocument();
    });
    const user = userEvent.setup();
    const input = screen.getByPlaceholderText("Filter by provider key…");
    await user.type(input, "baidu");
    await waitFor(() => {
      expect(listLinksMock).toHaveBeenCalledWith(1, 20, "baidu", undefined);
    });
    await userEvent.click(screen.getByRole("button", { name: "Export JSON" }));
    await waitFor(() => {
      expect(exportLinksMock).toHaveBeenCalledWith("json", "baidu", undefined);
    });
  });

  it("calls exportLinks with current status filter", async () => {
    render(<LinkList />);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Export JSON" })).toBeInTheDocument();
    });
    const user = userEvent.setup();
    const select = screen.getByRole("combobox");
    await user.selectOptions(select, "needs_password");
    await waitFor(() => {
      expect(listLinksMock).toHaveBeenCalledWith(1, 20, undefined, "needs_password");
    });
    await userEvent.click(screen.getByRole("button", { name: "Export JSON" }));
    await waitFor(() => {
      expect(exportLinksMock).toHaveBeenCalledWith("json", undefined, "needs_password");
    });
  });

  it("disables export buttons when total is 0", async () => {
    listLinksMock.mockResolvedValueOnce({ items: [], total: 0, page: 1, limit: 20 });
    render(<LinkList />);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Export JSON" })).toBeDisabled();
      expect(screen.getByRole("button", { name: "Export CSV" })).toBeDisabled();
    });
  });

  it("shows pagination when multiple pages", async () => {
    const multiPageResponse: LinkListResponse = {
      items: mockRecords,
      total: 50,
      page: 1,
      limit: 20,
    };
    listLinksMock.mockResolvedValueOnce(multiPageResponse);
    render(<LinkList />);
    await waitFor(() => {
      expect(screen.getByText("Page 1 of 3 (50 total)")).toBeInTheDocument();
      expect(screen.getByRole("button", { name: "Previous page" })).toBeInTheDocument();
      expect(screen.getByRole("button", { name: "Next page" })).toBeInTheDocument();
    });
  });

  it("disables previous button on first page when pagination exists", async () => {
    const multiPageResponse: LinkListResponse = {
      items: mockRecords,
      total: 50,
      page: 1,
      limit: 20,
    };
    listLinksMock.mockResolvedValueOnce(multiPageResponse);
    render(<LinkList />);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Previous page" })).toBeDisabled();
    });
  });

  it("renders badges with correct status", async () => {
    render(<LinkList />);
    await waitFor(() => {
      expect(screen.getByText("parsed")).toBeInTheDocument();
      expect(screen.getByText("needs_password")).toBeInTheDocument();
    });
  });

  it("filters by provider when input changes", async () => {
    render(<LinkList />);
    await waitFor(() => {
      expect(screen.getByText("baidu")).toBeInTheDocument();
    });
    const user = userEvent.setup();
    const input = screen.getByPlaceholderText("Filter by provider key…");
    await user.type(input, "baidu");
    await waitFor(() => {
      expect(listLinksMock).toHaveBeenCalledWith(1, 20, "baidu", undefined);
    });
  });

  it("filters by status when select changes", async () => {
    render(<LinkList />);
    await waitFor(() => {
      expect(screen.getByText("baidu")).toBeInTheDocument();
    });
    const user = userEvent.setup();
    const select = screen.getByRole("combobox");
    await user.selectOptions(select, "needs_password");
    await waitFor(() => {
      expect(listLinksMock).toHaveBeenCalledWith(1, 20, undefined, "needs_password");
    });
  });

  it("resets page to 1 when provider filter changes", async () => {
    render(<LinkList />);
    await waitFor(() => {
      expect(screen.getByText("baidu")).toBeInTheDocument();
    });
    const user = userEvent.setup();
    const input = screen.getByPlaceholderText("Filter by provider key…");
    await user.type(input, "baidu");
    await waitFor(() => {
      expect(listLinksMock).toHaveBeenLastCalledWith(1, 20, "baidu", undefined);
    });
  });

  it("triggers reload on refreshTrigger change", async () => {
    const { rerender } = render(<LinkList refreshTrigger={0} />);
    await waitFor(() => {
      expect(screen.getByText("baidu")).toBeInTheDocument();
    });
    listLinksMock.mockClear();
    listLinksMock.mockResolvedValueOnce(mockResponse);
    rerender(<LinkList refreshTrigger={1} />);
    await waitFor(() => {
      expect(listLinksMock).toHaveBeenCalledTimes(1);
    });
  });
});

