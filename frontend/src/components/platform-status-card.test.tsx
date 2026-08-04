import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { PlatformStatusCard } from "./platform-status-card";

describe("PlatformStatusCard", () => {
  it("renders implemented capability evidence when ready", () => {
    render(
      <PlatformStatusCard
        status={{
          kind: "ready",
          platform: {
            product: "Agentic Platform Baseline",
            short_name: "APB",
            version: "0.1.0",
            phase: "foundation",
            north_star: "Evidence first.",
            implemented_capabilities: ["api", "web"],
            deferred_capabilities: ["agents"],
          },
        }}
      />,
    );

    expect(screen.getByText("Control plane available")).toBeInTheDocument();
    expect(screen.getByText("2 capabilities")).toBeInTheDocument();
  });

  it("explains a degraded dependency state", () => {
    render(
      <PlatformStatusCard
        status={{ kind: "degraded", message: "Database unavailable." }}
      />,
    );

    expect(screen.getByText("Control plane degraded")).toBeInTheDocument();
    expect(screen.getByText("Dependency recovering")).toBeInTheDocument();
  });

  it("explains a completely unavailable API state", () => {
    render(
      <PlatformStatusCard
        status={{ kind: "unavailable", message: "API unavailable." }}
      />,
    );

    expect(screen.getByText("Control plane unavailable")).toBeInTheDocument();
    expect(screen.getByText("Local interface mode")).toBeInTheDocument();
  });
});
