import { describe, expect, it, vi } from "vitest";

import { getPlatformStatus } from "./platform";

const platformPayload = {
  product: "Agentic Platform Baseline",
  short_name: "APB",
  version: "0.1.0",
  phase: "foundation",
  north_star: "Evidence is the source of truth.",
  implemented_capabilities: ["operational-api"],
  deferred_capabilities: ["agent-orchestration"],
};

describe("getPlatformStatus", () => {
  it("returns validated platform information for a healthy response", async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue(
      new Response(JSON.stringify(platformPayload), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    const result = await getPlatformStatus(fetcher, "http://api:8000/");

    expect(result).toEqual({ kind: "ready", platform: platformPayload });
    expect(fetcher).toHaveBeenCalledWith(
      "http://api:8000/api/v1/platform",
      expect.objectContaining({ cache: "no-store" }),
    );
  });

  it("reports a degraded dependency response", async () => {
    const fetcher = vi
      .fn<typeof fetch>()
      .mockResolvedValue(new Response(null, { status: 503 }));

    await expect(getPlatformStatus(fetcher, "http://api")).resolves.toEqual({
      kind: "degraded",
      message: "The control plane is waiting for a required dependency.",
    });
  });

  it("reports an unsuccessful HTTP response", async () => {
    const fetcher = vi
      .fn<typeof fetch>()
      .mockResolvedValue(new Response(null, { status: 500 }));

    await expect(getPlatformStatus(fetcher, "http://api")).resolves.toEqual({
      kind: "unavailable",
      message: "The control plane status could not be verified.",
    });
  });

  it("rejects a response outside the versioned contract", async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue(
      new Response(JSON.stringify({ product: "incomplete" }), {
        status: 200,
      }),
    );

    await expect(getPlatformStatus(fetcher, "http://api")).resolves.toEqual({
      kind: "unavailable",
      message:
        "The control plane response does not satisfy the expected contract.",
    });
  });

  it("reports a network failure without leaking its cause", async () => {
    const fetcher = vi
      .fn<typeof fetch>()
      .mockRejectedValue(new Error("connection details"));

    await expect(getPlatformStatus(fetcher, "http://api")).resolves.toEqual({
      kind: "unavailable",
      message: "The control plane is not running in this environment yet.",
    });
  });
});
