import { useEffect, useState } from "react";
import { LinkRecord, LinkListResponse, ParseStatus, api } from "../api/client";

export interface LinkListProps {
  refreshTrigger?: number;
}

export default function LinkList({ refreshTrigger = 0 }: LinkListProps) {
  const [data, setData] = useState<LinkListResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [providerFilter, setProviderFilter] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<ParseStatus | string>("");
  const [isExporting, setIsExporting] = useState(false);

  const load = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await api.listLinks(page, 20, providerFilter || undefined, statusFilter || undefined);
      setData(resp);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load links");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, providerFilter, statusFilter, refreshTrigger]);

  const handleStatusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setStatusFilter(e.target.value as ParseStatus | "");
    setPage(1);
  };

  const handleProviderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setProviderFilter(e.target.value);
    setPage(1);
  };

  const handleExport = async (format: "json" | "csv") => {
    setIsExporting(true);
    try {
      const blob = await api.exportLinks(format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `nexus-observatory-export.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : `Failed to export ${format.toUpperCase()}`);
    } finally {
      setIsExporting(false);
    }
  };

  if (error) {
    return <p className="link-list link-list--error" role="alert">Error: {error}</p>;
  }

  const items: LinkRecord[] = data?.items ?? [];
  const total = data?.total ?? 0;
  const limit = data?.limit ?? 20;
  const totalPages = Math.max(1, Math.ceil(total / limit));

  return (
    <div className="link-list">
      <header className="link-list__header">
        <h2>Catalog</h2>
        <div className="link-list__actions">
          <button
            className="btn btn--secondary"
            onClick={() => handleExport("json")}
            disabled={isExporting || total === 0}
            aria-busy={isExporting}
          >
            {isExporting ? "Exporting…" : "Export JSON"}
          </button>
          <button
            className="btn btn--secondary"
            onClick={() => handleExport("csv")}
            disabled={isExporting || total === 0}
            aria-busy={isExporting}
          >
            {isExporting ? "Exporting…" : "Export CSV"}
          </button>
        </div>
      </header>

      <div className="link-list__filters">
        <label className="link-list__filter">
          <span>Provider</span>
          <input
            type="text"
            placeholder="Filter by provider key…"
            value={providerFilter}
            onChange={handleProviderChange}
            className="link-list__input"
          />
        </label>
        <label className="link-list__filter">
          <span>Status</span>
          <select
            value={statusFilter}
            onChange={handleStatusChange}
            className="link-list__input"
          >
            <option value="">All</option>
            <option value="parsed">parsed</option>
            <option value="needs_password">needs_password</option>
            <option value="unsupported">unsupported</option>
            <option value="error">error</option>
          </select>
        </label>
      </div>

      {isLoading ? (
        <p className="link-list__loading">Loading…</p>
      ) : items.length === 0 ? (
        <p className="link-list__empty">No records yet. Parse a share URL to get started.</p>
      ) : (
        <>
          <table className="link-list__table" role="grid">
            <thead>
              <tr>
                <th scope="col">Provider</th>
                <th scope="col">Resource ID</th>
                <th scope="col">Status</th>
                <th scope="col">Confidence</th>
                <th scope="col">Created (UTC)</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td>{item.provider}</td>
                  <td>
                    <code className="link-list__code">{item.resource_id}</code>
                  </td>
                  <td>
                    <span className={`badge badge--${item.status}`}>{item.status}</span>
                  </td>
                  <td>{item.confidence.toFixed(2)}</td>
                  <td>{item.created_at}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {totalPages > 1 && (
            <nav className="link-list__pagination" aria-label="Pagination">
              <button
                className="btn btn--ghost"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                aria-label="Previous page"
              >
                Previous
              </button>
              <span className="link-list__page-info">
                Page {page} of {totalPages} ({total} total)
              </span>
              <button
                className="btn btn--ghost"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                aria-label="Next page"
              >
                Next
              </button>
            </nav>
          )}
        </>
      )}
    </div>
  );
}