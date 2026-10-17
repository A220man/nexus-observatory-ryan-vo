import { useEffect, useState } from "react";
import { api, ApiError, LinkRecord, ProviderInfo, ParseResult } from "../api/client";
import LinkForm from "../components/LinkForm";
import LinkResult from "../components/LinkResult";
import LinkList from "../components/LinkList";
import ProviderCard from "../components/ProviderCard";

export default function ObservatoryDashboard() {
  const [activeTab, setActiveTab] = useState<"parse" | "catalog" | "providers">("parse");
  const [result, setResult] = useState<ParseResult | null>(null);
  const [isParsing, setIsParsing] = useState(false);
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [isProvidersLoading, setIsProvidersLoading] = useState(false);
  const [isProvidersError, setIsProvidersError] = useState<string | null>(null);
  const [refreshCatalog, setRefreshCatalog] = useState(0);

  const handleParseResult = (r: ParseResult) => {
    setResult(r);
    setRefreshCatalog((n) => n + 1);
    setIsParsing(false);
  };

  useEffect(() => {
    setIsProvidersLoading(true);
    api
      .getProviders()
      .then(setProviders)
      .catch((err) => {
        setIsProvidersError(
          err instanceof ApiError ? err.message : "Failed to load providers",
        );
      })
      .finally(() => setIsProvidersLoading(false));
  }, []);

  const record: LinkRecord | null = result?.record ?? null;
  const classification = result?.classification ?? null;
  const parseError = result?.error ?? null;

  return (
    <div className="dashboard">
      <nav className="dashboard__tabs">
        <button
          className={`tab ${activeTab === "parse" ? "tab--active" : ""}`}
          onClick={() => setActiveTab("parse")}
        >
          Parse
        </button>
        <button
          className={`tab ${activeTab === "catalog" ? "tab--active" : ""}`}
          onClick={() => setActiveTab("catalog")}
        >
          Catalog
        </button>
        <button
          className={`tab ${activeTab === "providers" ? "tab--active" : ""}`}
          onClick={() => setActiveTab("providers")}
        >
          Providers
        </button>
      </nav>

      {activeTab === "parse" && (
        <section className="dashboard__section">
          <LinkForm onResult={handleParseResult} onLoadingChange={setIsParsing} />
          <LinkResult
            record={record}
            classification={classification}
            error={parseError}
            isLoading={isParsing}
          />
        </section>
      )}

      {activeTab === "catalog" && (
        <section className="dashboard__section">
          <LinkList refreshTrigger={refreshCatalog} />
        </section>
      )}

      {activeTab === "providers" && (
        <section className="dashboard__section">
          {isProvidersError ? (
            <p role="alert">Error: {isProvidersError}</p>
          ) : isProvidersLoading ? (
            <p>Loading providers…</p>
          ) : (
            <div className="provider-grid">
              {providers.map((p) => (
                <ProviderCard key={p.key} provider={p} />
              ))}
            </div>
          )}
        </section>
      )}
    </div>
  );
}