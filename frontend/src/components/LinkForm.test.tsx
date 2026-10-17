/**
 * Tests for the LinkForm component.
 *
 * The `api` module is mocked so no real network calls are made.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import LinkForm from "./LinkForm";
import { ParseResult, LinkRecord } from "../api/client";

vi.mock("../api/client", () => ({
  api: {
    parseLink: vi.fn(),
    classify: vi.fn(),
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

// Access the mocked functions with proper typing.
import { api } from "../api/client";
const parseLinkMock = vi.mocked(api.parseLink);
const classifyMock = vi.mocked(api.classify);

const mockRecord = {
  id: 1,
  input_url: "https://pan.baidu.com/s/1abc",
  provider: "baidu",
  resource_id: "1abc",
  password: "",
  direct_link: "",
  strategy: "test",
  status: "parsed" as const,
  confidence: 0.9,
  error: null,
  created_at: "2026-01-01T00:00:00Z",
};

const mockClassification = {
  provider: "baidu",
  confidence: 0.95,
  probabilities: { baidu: 0.95 },
};

function mockParseSuccess() {
  parseLinkMock.mockResolvedValueOnce(mockRecord);
  classifyMock.mockResolvedValueOnce(mockClassification);
}

function mockParseError(message: string) {
  parseLinkMock.mockRejectedValueOnce(new Error(message));
}

describe("<LinkForm>", () => {
  const onResult = vi.fn();
  const onLoadingChange = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders an empty input and a Parse button", () => {
    render(<LinkForm onResult={onResult} />);
    expect(screen.getByRole("button", { name: "Parse" })).toBeInTheDocument();
    expect(screen.getByLabelText("Share URL")).toBeInTheDocument();
  });

  it("disables the button when the input is empty", () => {
    render(<LinkForm onResult={onResult} />);
    expect(screen.getByRole("button", { name: "Parse" })).toBeDisabled();
  });

  it("submits a URL and calls onResult with the parsed record", async () => {
    const user = userEvent.setup();
    mockParseSuccess();
    render(<LinkForm onResult={onResult} onLoadingChange={onLoadingChange} />);

    const input = screen.getByLabelText("Share URL");
    await user.type(input, "https://pan.baidu.com/s/1abc");

    await user.click(screen.getByRole("button", { name: "Parse" }));

    await waitFor(() => {
      expect(parseLinkMock).toHaveBeenCalledWith("https://pan.baidu.com/s/1abc");
    });
    await waitFor(() => {
      expect(onResult).toHaveBeenCalledTimes(1);
      const result: ParseResult = onResult.mock.calls[0][0];
      expect(result.record?.provider).toBe("baidu");
      expect(result.classification?.provider).toBe("baidu");
      expect(result.error).toBeNull();
    });
    expect(onLoadingChange).toHaveBeenCalledWith(true);
    expect(onLoadingChange).toHaveBeenCalledWith(false);
  });

  it("shows an error when parse fails", async () => {
    const user = userEvent.setup();
    mockParseError("API 400: Bad Request");
    render(<LinkForm onResult={onResult} onLoadingChange={onLoadingChange} />);

    const input = screen.getByLabelText("Share URL");
    await user.type(input, "https://bad.example.com/share/x");

    await user.click(screen.getByRole("button", { name: "Parse" }));

    await waitFor(() => {
      expect(screen.getByText(/API 400/)).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(onResult).toHaveBeenCalledTimes(1);
      const result: ParseResult = onResult.mock.calls[0][0];
      expect(result.record).toBeNull();
      expect(result.error).toBe("API 400: Bad Request");
    });
  });

  it("shows loading state and disables input during submission", async () => {
    const user = userEvent.setup();
    const { promise: parsePromise, resolve: resolveParse } = Promise.withResolvers<LinkRecord>();
    parseLinkMock.mockImplementation(() => parsePromise);

    render(<LinkForm onResult={onResult} />);

    const input = screen.getByLabelText("Share URL") as HTMLInputElement;
    await user.type(input, "https://pan.baidu.com/s/1abc");

    await user.click(screen.getByRole("button", { name: "Parse" }));

    // During submission: button shows "Parsing…" and is disabled, input is disabled
    expect(await screen.findByText("Parsing…")).toBeInTheDocument();
    expect(input).toBeDisabled();

    // Resolve and verify normal state returns
    resolveParse(mockRecord);
    classifyMock.mockResolvedValueOnce(mockClassification);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Parse" })).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(input).not.toBeDisabled();
    });
  });

});