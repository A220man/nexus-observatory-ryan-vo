import { ProviderInfo } from "../api/client";

export interface ProviderCardProps {
  provider: ProviderInfo;
}

export default function ProviderCard({ provider }: ProviderCardProps) {
  return (
    <div className="provider-card">
      <div className="provider-card__header">
        <span className="provider-card__key">#{provider.key}</span>
        <h3 className="provider-card__name">{provider.name}</h3>
      </div>
      {provider.password_param && (
        <p className="provider-card__row">
          <span className="provider-card__label">Password param:</span>{" "}
          {provider.password_param}
        </p>
      )}
      <p className="provider-card__row">
        <span className="provider-card__label">Domains:</span>{" "}
        {provider.domains.join(", ")}
      </p>
      <p className="provider-card__strategy">{provider.strategy}</p>
    </div>
  );
}