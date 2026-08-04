"""Pure policy checks for sensitive repository paths and content."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import PurePosixPath

SAFE_TEMPLATE_NAMES = frozenset(
    {
        ".env.example",
        ".firebaserc.example",
        "kubeconfig.example",
    }
)
BLOCKED_DIRECTORY_NAMES = frozenset(
    {
        ".gcloud",
        ".kube",
        ".secrets",
        ".ssh",
        "credentials",
        "secrets",
    }
)
BLOCKED_EXACT_NAMES = frozenset(
    {
        ".firebaserc",
        ".runtimeconfig.json",
        ".terraformrc",
        "application_default_credentials.json",
        "credentials.json",
        "id_ecdsa",
        "id_ed25519",
        "id_rsa",
        "terraform.rc",
    }
)
BLOCKED_PRIVATE_SUFFIXES = (
    ".jks",
    ".kdbx",
    ".key",
    ".keystore",
    ".p12",
    ".p8",
    ".pem",
    ".pfx",
)

CONTENT_PATTERNS = (
    (
        "private key material",
        re.compile(b"-----BEGIN " + b"(?:RSA |EC |OPENSSH |DSA )?" + b"PRIVATE KEY-----"),
    ),
    ("Google API key", re.compile(rb"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("GitHub token", re.compile(rb"\bgh[opsu]_[0-9A-Za-z]{36,}\b")),
    ("GitHub fine-grained token", re.compile(rb"\bgithub_pat_[0-9A-Za-z_]{82,}\b")),
    ("AWS access key", re.compile(rb"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("Slack token", re.compile(rb"\bxox[baprs]-[0-9A-Za-z-]{20,}\b")),
    ("Stripe secret key", re.compile(rb"\bsk_(?:live|test)_[0-9A-Za-z]{16,}\b")),
)
SERVICE_ACCOUNT_TYPE = re.compile(rb'"type"\s*:\s*"service_account"')
SERVICE_ACCOUNT_PRIVATE_KEY = re.compile(rb'"private_key"\s*:')


@dataclass(frozen=True, slots=True)
class Finding:
    """A policy finding that never contains the detected secret value."""

    path: str
    reason: str


def normalize_repository_path(path: str) -> str:
    """Normalize a repository-relative path for case-insensitive policy checks."""
    normalized = path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.casefold()


def is_forbidden_path(path: str) -> bool:
    """Return whether a path is too likely to contain private or local state."""
    normalized = normalize_repository_path(path)
    parsed = PurePosixPath(normalized)
    basename = parsed.name

    if (
        basename in SAFE_TEMPLATE_NAMES
        or basename.endswith(".env.example")
        or (basename.startswith(".env.") and basename.endswith(".example"))
    ):
        return False
    if any(part in BLOCKED_DIRECTORY_NAMES for part in parsed.parts):
        return True
    if (
        basename == ".env"
        or basename.startswith(".env.")
        or basename.endswith(".env")
        or ".env." in basename
    ):
        return True
    if basename in BLOCKED_EXACT_NAMES or basename.startswith("kubeconfig."):
        return True
    if basename.endswith(BLOCKED_PRIVATE_SUFFIXES):
        return True
    if (
        basename.endswith((".tfstate", ".tfvars", ".tfvars.json", ".tfplan"))
        or ".tfstate." in basename
    ):
        return True
    return bool(
        re.fullmatch(r"(?:service[-_]account.*|.*firebase-adminsdk.*)\.json", basename)
        or re.fullmatch(r"(?:client_secret|oauth-client).+\.json", basename)
    )


def find_sensitive_content(content: bytes) -> tuple[str, ...]:
    """Return high-confidence secret categories without returning secret values."""
    matches = [name for name, pattern in CONTENT_PATTERNS if pattern.search(content)]
    if SERVICE_ACCOUNT_TYPE.search(content) and SERVICE_ACCOUNT_PRIVATE_KEY.search(content):
        matches.append("Google service-account key")
    return tuple(matches)


def scan_entries(entries: Iterable[tuple[str, bytes]]) -> tuple[Finding, ...]:
    """Scan repository entries for forbidden paths and high-confidence content."""
    findings: list[Finding] = []
    for path, content in entries:
        if is_forbidden_path(path):
            findings.append(Finding(path=path, reason="forbidden sensitive path"))
        findings.extend(
            Finding(path=path, reason=f"sensitive content: {category}")
            for category in find_sensitive_content(content)
        )
    return tuple(findings)
