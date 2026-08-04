import { PlatformStatusCard } from "@/components/platform-status-card";
import { getPlatformStatus } from "@/lib/platform";

const deliveryFlow = [
  { number: "01", label: "Configure", detail: "Identity and environment" },
  { number: "02", label: "Specify", detail: "Versioned requirements" },
  { number: "03", label: "Build", detail: "Isolated workspace" },
  { number: "04", label: "Verify", detail: "Tests and security" },
  { number: "05", label: "Promote", detail: "Human approval gate" },
];

const foundations = [
  {
    eyebrow: "Contracts",
    title: "Spec-driven by default",
    copy: "Requirements, decisions, and acceptance criteria remain versioned beside the code.",
  },
  {
    eyebrow: "Isolation",
    title: "Tenant-aware from day one",
    copy: "Trusted identity, forced row-level security, and separate execution boundaries reduce blast radius.",
  },
  {
    eyebrow: "Evidence",
    title: "Verification before promotion",
    copy: "Builds, tests, dependency review, and security findings are deterministic release evidence.",
  },
  {
    eyebrow: "Extension",
    title: "Provider-neutral boundaries",
    copy: "Vertical domains, AgentOps, and MLOps extend explicit contracts instead of coupling to vendors.",
  },
];

export default async function Home() {
  const apiBaseUrl =
    process.env.PLATFORM_API_BASE_URL ?? "http://localhost:8000";
  const platformStatus = await getPlatformStatus(fetch, apiBaseUrl);

  return (
    <main>
      <header className="site-header">
        <a
          className="wordmark"
          href="#start"
          aria-label="Agentic Platform Baseline, return to start"
        >
          <span className="wordmark-mark" aria-hidden="true">
            A
          </span>
          <span>APB</span>
        </a>
        <div className="header-meta">
          <span className="phase-dot" aria-hidden="true" />
          Template foundation · 0.1
        </div>
      </header>

      <section className="hero" id="start" aria-labelledby="hero-title">
        <div className="hero-copy">
          <p className="kicker">Reusable agentic platform foundation</p>
          <h1 id="hero-title">
            Build the vertical.
            <span>Keep the foundation verifiable.</span>
          </h1>
          <p className="hero-lede">
            A provider-neutral baseline for multi-tenant products that need
            explicit contracts, secure delivery, and evidence at every promotion
            gate.
          </p>
          <a className="text-link" href="#foundations">
            Explore the foundation <span aria-hidden="true">↓</span>
          </a>
        </div>

        <aside className="north-star" aria-label="Template north star">
          <p className="north-star-label">North star</p>
          <p>
            Start new product verticals from a secure, observable, and
            maintainable platform without inheriting another product&apos;s
            business rules.
          </p>
          <div className="north-star-footer">
            <span>Human governed</span>
            <span>Evidence first</span>
          </div>
        </aside>
      </section>

      <section className="flow-section" aria-labelledby="flow-title">
        <div className="section-heading">
          <p className="kicker">Adoption path</p>
          <h2 id="flow-title">
            One repeatable path from configuration to promotion.
          </h2>
        </div>
        <ol className="delivery-flow">
          {deliveryFlow.map((stage) => (
            <li key={stage.number}>
              <span className="flow-number">{stage.number}</span>
              <strong>{stage.label}</strong>
              <span>{stage.detail}</span>
            </li>
          ))}
        </ol>
      </section>

      <section
        className="foundation-section"
        id="foundations"
        aria-labelledby="foundation-title"
      >
        <div className="section-heading">
          <p className="kicker">Template foundation</p>
          <h2 id="foundation-title">
            Shared engineering controls, not shared business logic.
          </h2>
          <p>
            The baseline provides operational and security boundaries while
            every derived project owns its domain, product experience, and
            deployment choices.
          </p>
        </div>

        <div className="foundation-grid">
          {foundations.map((foundation) => (
            <article key={foundation.title}>
              <p className="card-eyebrow">{foundation.eyebrow}</p>
              <h3>{foundation.title}</h3>
              <p>{foundation.copy}</p>
            </article>
          ))}
        </div>
      </section>

      <section
        className="operational-section"
        aria-labelledby="operational-title"
      >
        <div className="section-heading compact-heading">
          <p className="kicker">Control plane</p>
          <h2 id="operational-title">
            The baseline reports its real capabilities.
          </h2>
          <p>
            Implemented foundation behavior remains distinct from deferred
            AgentOps, MLOps, provider execution, and vertical-specific
            capabilities.
          </p>
        </div>
        <PlatformStatusCard status={platformStatus} />
      </section>

      <footer>
        <p>Agentic Platform Baseline</p>
        <p>Local-first · GCP-ready · Human-gated promotion</p>
      </footer>
    </main>
  );
}
