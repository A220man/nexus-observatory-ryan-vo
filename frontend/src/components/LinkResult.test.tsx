/**
 * Tests for the LinkResult component.
 */
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import LinkResult from "./LinkResult";
import { LinkRecord } from "../api/client";

const mockRecord: LinkRecord = {
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
};

const mockClassification = {
  provider: "baidu",
  confidence: 0.9,
  probabilities: { baidu: 0.9 },
};

describe("<LinkResult>", () => {
  it("shows loading state when isLoading is true", () => {
    render(<LinkResult record={null} classification={null} error={null} isLoading={true} />);
    expect(screen.getByText("Parsing…")).toBeInTheDocument();
  });

  it("shows error state when error is provided", () => {
    render(<LinkResult record={null} classification={null} error="API failed" isLoading={false} />);
    expect(screen.getByRole("alert")).toBeInTheDocument();
    expect(screen.getByText("API failed")).toBeInTheDocument();
  });

  it("shows empty state when no record and no error", () => {
    render(<LinkResult record={null} classification={null} error={null} isLoading={false} />);
    expect(screen.getByText(/Enter a share URL/)).toBeInTheDocument();
  });

  it("renders provider, resource_id, password, status, and confidence", () => {
    render(
      <LinkResult
        record={mockRecord}
        classification={mockClassification}
        error={null}
        isLoading={false}
      />
    );
    expect(screen.getByText("baidu")).toBeInTheDocument();
    expect(screen.getByText("1abc")).toBeInTheDocument();
    expect(screen.getByText("1234")).toBeInTheDocument();
    expect(screen.getByText("parsed")).toBeInTheDocument();
    expect(screen.getByText("95.0%")).toBeInTheDocument();
  });

  it("renders ML prediction when classification is provided", () => {
    render(
      <LinkResult
        record={mockRecord}
        classification={mockClassification}
        error={null}
        isLoading={false}
      />
    );
    expect(screen.getByText("ML Prediction")).toBeInTheDocument();
    expect(screen.getByText(/baidu \(90.0%\)/)).toBeInTheDocument();
  });

  it("renders strategy when present", () => {
    render(
      <LinkResult
        record={mockRecord}
        classification={null}
        error={null}
        isLoading={false}
      />
    );
    expect(screen.getByText("Strategy")).toBeInTheDocument();
    expect(screen.getByText("redirect")).toBeInTheDocument();
  });

  it("renders record error when present", () => {
    const recordWithError: LinkRecord = {
      ...mockRecord,
      error: "Something went wrong",
    };
    render(
      <LinkResult
        record={recordWithError}
        classification={null}
        error={null}
        isLoading={false}
      />
    );
    expect(screen.getByText("Error")).toBeInTheDocument();
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
  });

  it("hides password row when password is empty", () => {
    const recordNoPassword: LinkRecord = {
      ...mockRecord,
      password: "",
    };
    render(
      <LinkResult
        record={recordNoPassword}
        classification={null}
        error={null}
        isLoading={false}
      />
    );
    expect(screen.queryByText("Password")).not.toBeInTheDocument();
  });

  it("shows unknown provider when provider is empty", () => {
    const recordUnknownProvider: LinkRecord = {
      ...mockRecord,
      provider: "",
    };
    render(
      <LinkResult
        record={recordUnknownProvider}
        classification={null}
        error={null}
        isLoading={false}
      />
    );
    expect(screen.getByText("unknown")).toBeInTheDocument();
  });
});
