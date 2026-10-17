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

  if (error) {
    return <p className="link-list link-list--error" role="alert">Error: {error}</p>;
  }

  const items: LinkRecord[] = data?.items ?? [];
  const total = data?.total ?? 0;
  const limit = data?.limit ?? 20;

  return (
    <div className="link-list">
      <div className="link-list__filters">
        <input
          type="text"
          placeholder="Filter by provider…"
          value={providerFilter}
          onChange={handleProviderChange}
          className="filter-input"
          aria-label="Filter by provider"
        />
        <select
          value={statusFilter}
          onChange={handleStatusChange}
          className="filter-select"
          aria-label="Filter by status"
        >
          <option value="">All statuses</option>
          <option value="parsed">parsed</option>
          <option value="needs_password">needs_password</option>
          <option value="unsupported">unsupported</option>
          <option value="error">error</option>
        </select>
      </div>

      {isLoading ? (
        <p className="link-list__loading">Loading…</p>
      ) : items.length === 0 ? (
        <p className="link-list__empty">No links found.</p>
      ) : (
        <>
          <table className="link-table">
            <thead>
              <tr>
                <th>#ID</th>
                <th>Provider</th>
                <th>Resource ID</th>
                <th>Status</th>
                <th>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td className="font-mono">{item.id}</td>
                  <td>{item.provider || "unknown"}</td>
                  <td className="font-mono">{item.resource_id.slice(0, 20)}{item.resource_id.length > 20 && "…"}</td>
                  <td>{item.status}</td>
                  <td>{(item.confidence * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="link-list__pagination">
            <button
              className="btn btn--outline"
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
            >
              ← Prev
            </button>
            <span>Page {page} of {Math.max(1, Math.ceil(total / limit))}</span>
            <button
              className="btn btn--outline"
              onClick={() => setPage(page + 1)}
              disabled={page * limit >= total}
            >
              Next →
            </button>
          </div>
        </>
      )}
    </div>
  );
}