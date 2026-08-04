import { z } from "zod";

const platformInfoSchema = z.object({
  product: z.string(),
  short_name: z.string(),
  version: z.string(),
  phase: z.literal("foundation"),
  north_star: z.string(),
  implemented_capabilities: z.array(z.string()),
  deferred_capabilities: z.array(z.string()),
});

export type PlatformInfo = z.infer<typeof platformInfoSchema>;

export type PlatformStatus =
  | { kind: "ready"; platform: PlatformInfo }
  | { kind: "degraded"; message: string }
  | { kind: "unavailable"; message: string };

export async function getPlatformStatus(
  fetcher: typeof fetch,
  apiBaseUrl: string,
): Promise<PlatformStatus> {
  const baseUrl = apiBaseUrl.replace(/\/+$/, "");

  try {
    const response = await fetcher(`${baseUrl}/api/v1/platform`, {
      cache: "no-store",
      signal: AbortSignal.timeout(2_000),
    });

    if (response.status === 503) {
      return {
        kind: "degraded",
        message: "The control plane is waiting for a required dependency.",
      };
    }

    if (!response.ok) {
      return {
        kind: "unavailable",
        message: "The control plane status could not be verified.",
      };
    }

    const parsed = platformInfoSchema.safeParse(await response.json());
    if (!parsed.success) {
      return {
        kind: "unavailable",
        message:
          "The control plane response does not satisfy the expected contract.",
      };
    }

    return { kind: "ready", platform: parsed.data };
  } catch {
    return {
      kind: "unavailable",
      message: "The control plane is not running in this environment yet.",
    };
  }
}
