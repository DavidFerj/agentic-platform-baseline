"""Validate repository secret-leak prevention controls."""

from __future__ import annotations

import argparse
import subprocess
from collections.abc import Iterable, Sequence
from pathlib import Path

from scripts.repository_hygiene import Finding, scan_entries

ROOT = Path(__file__).resolve().parents[1]

IGNORE_CANDIDATES = (
    ".env",
    "frontend/.env.production",
    "frontend/runtime.env.local",
    ".secrets/token.txt",
    "credentials/service-account.json",
    "gcp/private.key",
    "gcp/certificate.p12",
    "application_default_credentials.json",
    "gcp/firebase/.firebaserc",
    "gcp/firebase/.runtimeconfig.json",
    "gcp/firebase/example-firebase-adminsdk-local.json",
    "gcp/infrastructure/terraform/.terraform/providers.lock",
    "gcp/infrastructure/terraform/terraform.tfstate",
    "gcp/infrastructure/terraform/production.auto.tfvars",
    ".gcloud/credentials.db",
    ".kube/config",
)

REQUIRED_DOCKERIGNORE_PATTERNS = frozenset(
    {
        ".git",
        ".gcloud",
        ".kube",
        "**/.env",
        "**/.env.*",
        "**/*.env",
        "**/*.env.*",
        "**/.secrets",
        "**/secrets",
        "**/credentials",
        "**/.ssh",
        "**/*.pem",
        "**/*.key",
        "**/*.p12",
        "**/*.pfx",
        "**/application_default_credentials.json",
        "**/service-account*.json",
        "**/*-firebase-adminsdk-*.json",
        "**/.terraform",
        "**/*.tfstate",
        "**/*.tfstate.*",
        "**/*.tfvars",
        "**/*.tfvars.json",
        "**/.runtimeconfig.json",
        "**/.firebaserc",
        "**/apphosting.local.yaml",
    }
)
REQUIRED_GCLOUDIGNORE_LINES = frozenset(
    {
        ".gcloudignore",
        ".git",
        ".gitignore",
        "#!include:.gitignore",
    }
)


def run_git(
    arguments: Sequence[str],
    *,
    input_bytes: bytes | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[bytes]:
    """Run Git in the repository without invoking a shell."""
    return subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        input=input_bytes,
        capture_output=True,
        check=check,
    )


def parse_nul_paths(output: bytes) -> tuple[str, ...]:
    """Parse Git's NUL-delimited path output."""
    return tuple(part.decode("utf-8") for part in output.split(b"\0") if part)


def repository_paths(*, staged: bool) -> tuple[str, ...]:
    """Return staged paths or every path known to the index."""
    if staged:
        result = run_git(
            ["diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"],
        )
    else:
        result = run_git(["ls-files", "-z"])
    return parse_nul_paths(result.stdout)


def index_entries(paths: Iterable[str]) -> tuple[tuple[str, bytes], ...]:
    """Read path content from the Git index, not from potentially unsafe symlinks."""
    entries: list[tuple[str, bytes]] = []
    for path in paths:
        result = run_git(["show", f":{path}"])
        entries.append((path, result.stdout))
    return tuple(entries)


def ignored_candidates() -> frozenset[str]:
    """Return representative sensitive paths ignored by the effective Git policy."""
    input_bytes = b"\0".join(path.encode("utf-8") for path in IGNORE_CANDIDATES) + b"\0"
    result = run_git(
        ["check-ignore", "--no-index", "-z", "--stdin"],
        input_bytes=input_bytes,
        check=False,
    )
    if result.returncode not in {0, 1}:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
    return frozenset(parse_nul_paths(result.stdout))


def active_patterns(path: Path) -> frozenset[str]:
    """Return non-comment patterns while retaining gcloud's include directive."""
    lines = (line.strip() for line in path.read_text(encoding="utf-8").splitlines())
    return frozenset(
        line for line in lines if line and (not line.startswith("#") or line.startswith("#!"))
    )


def policy_findings(*, staged: bool) -> tuple[Finding, ...]:
    """Collect all content, path, and ignore-policy findings."""
    paths = repository_paths(staged=staged)
    findings = list(scan_entries(index_entries(paths)))

    ignored = ignored_candidates()
    findings.extend(
        Finding(path=path, reason="sensitive path is not ignored by .gitignore")
        for path in IGNORE_CANDIDATES
        if path not in ignored
    )

    docker_patterns = active_patterns(ROOT / ".dockerignore")
    findings.extend(
        Finding(path=".dockerignore", reason=f"missing pattern: {pattern}")
        for pattern in sorted(REQUIRED_DOCKERIGNORE_PATTERNS - docker_patterns)
    )

    gcloud_patterns = active_patterns(ROOT / ".gcloudignore")
    findings.extend(
        Finding(path=".gcloudignore", reason=f"missing line: {pattern}")
        for pattern in sorted(REQUIRED_GCLOUDIGNORE_LINES - gcloud_patterns)
    )
    return tuple(findings)


def main() -> None:
    """Run the hygiene gate and fail without echoing any secret values."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--staged",
        action="store_true",
        help="scan only staged files; ignore-policy invariants are always checked",
    )
    arguments = parser.parse_args()

    findings = policy_findings(staged=arguments.staged)
    if findings:
        details = "\n".join(f"- {finding.path}: {finding.reason}" for finding in findings)
        raise SystemExit(f"repository hygiene validation failed:\n{details}")
    scope = "staged files" if arguments.staged else "all tracked files"
    print(f"Repository hygiene validation passed for {scope}.")


if __name__ == "__main__":
    main()
