import { useState } from "react";
import { api, ApiError, ParseResult } from "../api/client";

export interface LinkFormProps {
  onResult: (result: ParseResult) => void;
  onLoadingChange?: (loading: boolean) => void;
}

export default function LinkForm({ onResult, onLoadingChange }: LinkFormProps) {
  const [url, setUrl] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    setIsSubmitting(true);
    onLoadingChange?.(true);
    setError(null);
    let errorMsg: string | null = null;

    try {
      const record = await api.parseLink(url.trim());
      try {
        const classification = await api.classify(url.trim());
        onResult({
          record,
          classification: {
            provider: classification.provider,
            confidence: classification.confidence,
          },
          error: null,
        });
      } catch {
        // Classify is advisory — still show the parsed record.
        onResult({ record, classification: null, error: null });
      }
    } catch (err) {
      errorMsg = err instanceof ApiError ? err.message : err instanceof Error ? err.message : "Unexpected error";
      setError(errorMsg);
      onResult({ record: null, classification: null, error: errorMsg });
    } finally {
      setIsSubmitting(false);
      onLoadingChange?.(false);
    }
  };

  return (
    <form className="link-form" onSubmit={handleSubmit}>
      <input
        type="url"
        placeholder="Paste a cloud-disk share URL…"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        disabled={isSubmitting}
        className="link-form__input"
        aria-label="Share URL"
      />
      <button
        type="submit"
        disabled={isSubmitting || !url.trim()}
        className="btn btn--accent"
        aria-busy={isSubmitting}
      >
        {isSubmitting ? "Parsing…" : "Parse"}
      </button>
      {error && <p className="link-form__error" role="alert">{error}</p>}
    </form>
  );
}