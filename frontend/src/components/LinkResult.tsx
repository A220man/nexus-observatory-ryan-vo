import { LinkRecord } from "../api/client";

export interface LinkResultProps {
  record: LinkRecord | null;
  classification: { provider: string; confidence: number } | null;
  error: string | null;
  isLoading: boolean;
}

const STATUS_COLORS: Record<string, string> = {
  parsed: "var(--success)",
  needs_password: "var(--warning)",
  unsupported: "var(--muted)",
  error: "var(--error)",
};

export default function LinkResult({
  record,
  classification,
  error,
  isLoading,
}: LinkResultProps) {
  if (isLoading) {
    return <p className="link-result link-result--loading">Parsing…</p>;
  }

  if (error) {
    return (
      <div className="link-result link-result--error" role="alert">
        <p className="link-result__label">Error</p>
        <p className="link-result__value">{error}</p>
      </div>
    );
  }

  if (!record) {
    return (
      <div className="link-result link-result--empty">
        <p>Enter a share URL and click Parse to see the result here.</p>
      </div>
    );
  }

  const statusColor = STATUS_COLORS[record.status] ?? "var(--muted)";

  return (
    <div className="link-result">
      <div className="link-result__row">
        <span className="link-result__label">Provider</span>
        <span className="link-result__value">{record.provider || "unknown"}</span>
      </div>
      <div className="link-result__row">
        <span className="link-result__label">Resource ID</span>
        <span className="link-result__value font-mono">{record.resource_id || "—"}</span>
      </div>
      {record.password && (
        <div className="link-result__row">
          <span className="link-result__label">Password</span>
          <span className="link-result__value font-mono">{record.password}</span>
        </div>
      )}
      <div className="link-result__row">
        <span className="link-result__label">Status</span>
        <span
          className="link-result__value"
          style={{ color: statusColor, fontWeight: 600 }}
        >
          {record.status}
        </span>
      </div>
      <div className="link-result__row">
        <span className="link-result__label">ML Confidence</span>
        <span className="link-result__value">
          {record.confidence !== undefined
            ? `${(record.confidence * 100).toFixed(1)}%`
            : "—"}
        </span>
      </div>
      {classification && classification.provider && (
        <div className="link-result__row">
          <span className="link-result__label">ML Prediction</span>
          <span className="link-result__value">
            {classification.provider} ({(classification.confidence * 100).toFixed(1)}%)
          </span>
        </div>
      )}
      {record.strategy && (
        <div className="link-result__row">
          <span className="link-result__label">Strategy</span>
          <span className="link-result__value">{record.strategy}</span>
        </div>
      )}
      {record.error && (
        <div className="link-result__row">
          <span className="link-result__label">Error</span>
          <span className="link-result__value" style={{ color: "var(--error)" }}>
            {record.error}
          </span>
        </div>
      )}
    </div>
  );
}