/**
 * Tests for the ProviderCard component.
 */
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import ProviderCard from "./ProviderCard";
import { ProviderInfo } from "../api/client";

const mockProvider: ProviderInfo = {
  key: "baidu",
  name: "Baidu Cloud",
  domains: ["pan.baidu.com", "yun.baidu.com"],
  password_param: "pwd",
  strategy: "redirect",
};

describe("<ProviderCard>", () => {
  it("renders provider key and name", () => {
    render(<ProviderCard provider={mockProvider} />);
    expect(screen.getByText("#baidu")).toBeInTheDocument();
    expect(screen.getByText("Baidu Cloud")).toBeInTheDocument();
  });

  it("renders password param when present", () => {
    render(<ProviderCard provider={mockProvider} />);
    expect(screen.getByText("Password param:")).toBeInTheDocument();
    expect(screen.getByText("pwd")).toBeInTheDocument();
  });

  it("renders domains list", () => {
    render(<ProviderCard provider={mockProvider} />);
    expect(screen.getByText("Domains:")).toBeInTheDocument();
    // Domains are joined with ", " so match the combined text
    expect(screen.getByText("pan.baidu.com, yun.baidu.com")).toBeInTheDocument();
  });

  it("renders strategy", () => {
    render(<ProviderCard provider={mockProvider} />);
    expect(screen.getByText("redirect")).toBeInTheDocument();
  });

  it("hides password param row when password_param is null", () => {
    const providerNoPassword: ProviderInfo = {
      ...mockProvider,
      password_param: null,
    };
    render(<ProviderCard provider={providerNoPassword} />);
    expect(screen.queryByText("Password param:")).not.toBeInTheDocument();
  });

  it("handles single domain", () => {
    const providerSingleDomain: ProviderInfo = {
      ...mockProvider,
      domains: ["single.domain.com"],
    };
    render(<ProviderCard provider={providerSingleDomain} />);
    expect(screen.getByText("Domains:")).toBeInTheDocument();
    expect(screen.getByText("single.domain.com")).toBeInTheDocument();
  });

  it("handles multiple domains", () => {
    const providerMultiDomain: ProviderInfo = {
      ...mockProvider,
      domains: ["a.com", "b.com", "c.com", "d.com"],
    };
    render(<ProviderCard provider={providerMultiDomain} />);
    expect(screen.getByText("Domains:")).toBeInTheDocument();
    expect(screen.getByText("a.com, b.com, c.com, d.com")).toBeInTheDocument();
  });
});
