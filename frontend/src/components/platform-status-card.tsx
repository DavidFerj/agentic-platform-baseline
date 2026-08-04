import type { PlatformStatus } from "@/lib/platform";

export function PlatformStatusCard({
  status,
}: Readonly<{ status: PlatformStatus }>) {
  if (status.kind === "ready") {
    return (
      <article className="status-card status-ready" aria-live="polite">
        <div>
          <p className="status-label">
            <span aria-hidden="true" />
            Control plane available
          </p>
          <h3>{status.platform.short_name} foundation</h3>
          <p>Version {status.platform.version} · API contract v1</p>
        </div>
        <dl>
          <div>
            <dt>Implemented</dt>
            <dd>
              {status.platform.implemented_capabilities.length} capabilities
            </dd>
          </div>
          <div>
            <dt>Phase</dt>
            <dd>{status.platform.phase}</dd>
          </div>
        </dl>
      </article>
    );
  }

  const degraded = status.kind === "degraded";
  return (
    <article
      className={`status-card ${degraded ? "status-degraded" : "status-unavailable"}`}
      role="status"
    >
      <div>
        <p className="status-label">
          <span aria-hidden="true" />
          {degraded ? "Control plane degraded" : "Control plane unavailable"}
        </p>
        <h3>{degraded ? "Dependency recovering" : "Local interface mode"}</h3>
        <p>{status.message}</p>
      </div>
      <p className="status-action">
        {degraded
          ? "The API responds, but a required dependency is not ready."
          : "Start the API service to enable live operational status."}
      </p>
    </article>
  );
}
