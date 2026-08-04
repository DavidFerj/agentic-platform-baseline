import {
  assertFails,
  assertSucceeds,
  initializeTestEnvironment,
  type RulesTestEnvironment,
} from "@firebase/rules-unit-testing";
import { doc, getDoc, setDoc } from "firebase/firestore";
import { readFile } from "node:fs/promises";
import { afterAll, beforeAll, beforeEach, describe, test } from "vitest";

let testEnvironment: RulesTestEnvironment;

function identityTenant(tenant: string) {
  return {
    firebase: {
      sign_in_provider: "custom" as const,
      tenant,
    },
  };
}

beforeAll(async () => {
  testEnvironment = await initializeTestEnvironment({
    projectId: "agentic-platform-local",
    firestore: {
      rules: await readFile(
        new URL("../firestore.rules", import.meta.url),
        "utf8",
      ),
    },
  });
});

beforeEach(async () => {
  await testEnvironment.clearFirestore();
  await testEnvironment.withSecurityRulesDisabled(async (context) => {
    await setDoc(
      doc(context.firestore(), "tenants/tenant-a/runProjections/run-a"),
      { status: "running" },
    );
    await setDoc(
      doc(context.firestore(), "tenants/tenant-b/runProjections/run-b"),
      { status: "queued" },
    );
    await setDoc(
      doc(context.firestore(), "tenants/tenant-a/projectProjections/project-a"),
      { status: "validated" },
    );
    await setDoc(doc(context.firestore(), "internalRuns/run-a"), {
      checkpoint: "sensitive",
    });
  });
});

afterAll(async () => {
  await testEnvironment.cleanup();
});

describe("Firestore tenant projections", () => {
  test("allows a tenant identity to read its own projection", async () => {
    const tenant = testEnvironment.authenticatedContext(
      "user-a",
      identityTenant("tenant-a"),
    );

    await assertSucceeds(
      getDoc(doc(tenant.firestore(), "tenants/tenant-a/runProjections/run-a")),
    );
    await assertSucceeds(
      getDoc(
        doc(
          tenant.firestore(),
          "tenants/tenant-a/projectProjections/project-a",
        ),
      ),
    );
  });

  test("denies cross-tenant reads", async () => {
    const tenant = testEnvironment.authenticatedContext(
      "user-a",
      identityTenant("tenant-a"),
    );

    await assertFails(
      getDoc(doc(tenant.firestore(), "tenants/tenant-b/runProjections/run-b")),
    );
  });

  test("denies unauthenticated and project-level reads", async () => {
    const unauthenticated = testEnvironment.unauthenticatedContext();
    const projectIdentity = testEnvironment.authenticatedContext("user-a");

    await assertFails(
      getDoc(
        doc(
          unauthenticated.firestore(),
          "tenants/tenant-a/runProjections/run-a",
        ),
      ),
    );
    await assertFails(
      getDoc(
        doc(
          projectIdentity.firestore(),
          "tenants/tenant-a/runProjections/run-a",
        ),
      ),
    );
  });

  test("denies every client write", async () => {
    const tenant = testEnvironment.authenticatedContext(
      "user-a",
      identityTenant("tenant-a"),
    );

    await assertFails(
      setDoc(
        doc(tenant.firestore(), "tenants/tenant-a/runProjections/run-new"),
        { status: "queued" },
      ),
    );
  });

  test("denies reads outside the projection allowlist", async () => {
    const tenant = testEnvironment.authenticatedContext(
      "user-a",
      identityTenant("tenant-a"),
    );

    await assertFails(getDoc(doc(tenant.firestore(), "internalRuns/run-a")));
  });
});
