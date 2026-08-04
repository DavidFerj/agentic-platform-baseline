const endpoint = "http://127.0.0.1:5002";
const response = await fetch(endpoint, {
  signal: AbortSignal.timeout(10_000),
});

if (!response.ok) {
  throw new Error(`App Hosting emulator returned HTTP ${response.status}`);
}

const body = await response.text();
if (!body.includes("Agentic Platform Baseline")) {
  throw new Error(
    "App Hosting emulator did not render the baseline application",
  );
}
