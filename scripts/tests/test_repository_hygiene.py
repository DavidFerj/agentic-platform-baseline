from __future__ import annotations

import pytest

from scripts.repository_hygiene import (
    Finding,
    find_sensitive_content,
    is_forbidden_path,
    normalize_repository_path,
    scan_entries,
)


@pytest.mark.parametrize(
    "path",
    [
        ".env",
        "frontend/.env.production",
        "frontend/runtime.env.local",
        "credentials/service-account.json",
        ".secrets/token.txt",
        ".gcloud/credentials.db",
        ".kube/config",
        "gcp/private.key",
        "gcp/certificate.p12",
        "gcp/infrastructure/terraform/terraform.tfstate",
        "gcp/infrastructure/terraform/terraform.tfstate.backup",
        "gcp/infrastructure/terraform/production.auto.tfvars",
        "gcp/infrastructure/terraform/release.tfplan",
        "application_default_credentials.json",
        "gcp/firebase/example-firebase-adminsdk-local.json",
        "service_account_prod.json",
        "client_secret_local.json",
        "oauth-client-production.json",
        "kubeconfig.production",
    ],
)
def test_forbidden_paths_cover_secret_and_infrastructure_state(path: str) -> None:
    assert is_forbidden_path(path)


@pytest.mark.parametrize(
    "path",
    [
        ".env.example",
        "frontend/.env.production.example",
        "frontend/runtime.env.example",
        ".firebaserc.example",
        "kubeconfig.example",
        "gcp/firebase/firestore.indexes.json",
        "gcp/infrastructure/terraform/main.tf",
    ],
)
def test_safe_templates_and_source_files_remain_trackable(path: str) -> None:
    assert not is_forbidden_path(path)


def test_normalize_repository_path_handles_windows_and_dot_prefixes() -> None:
    assert normalize_repository_path("./GCP\\Private.KEY") == "gcp/private.key"


def test_find_sensitive_content_reports_categories_without_values() -> None:
    private_key = b"-----BEGIN " + b"PRIVATE KEY-----"
    google_key = b"AIza" + (b"A" * 35)
    github_token = b"gho_" + (b"A" * 36)
    github_fine_grained = b"github_pat_" + (b"A" * 82)
    aws_key = b"AKIA" + (b"A" * 16)
    slack_token = b"xoxb-" + (b"A" * 24)
    stripe_key = b"sk_live_" + (b"A" * 20)
    service_account = b'{"type":' + b'"service_account",' + b'"private_' + b'key":"redacted"}'
    content = b"\n".join(
        (
            private_key,
            google_key,
            github_token,
            github_fine_grained,
            aws_key,
            slack_token,
            stripe_key,
            service_account,
        )
    )

    categories = find_sensitive_content(content)

    assert set(categories) == {
        "private key material",
        "Google API key",
        "GitHub token",
        "GitHub fine-grained token",
        "AWS access key",
        "Slack token",
        "Stripe secret key",
        "Google service-account key",
    }
    assert all(value.decode() not in repr(categories) for value in (google_key, github_token))


def test_service_account_requires_both_markers() -> None:
    type_marker = b'{"type":' + b'"service_account"}'
    key_marker = b'{"private_' + b'key":"redacted"}'
    assert find_sensitive_content(type_marker) == ()
    assert find_sensitive_content(key_marker) == ()


def test_scan_entries_combines_path_and_content_findings() -> None:
    token = b"ghu_" + (b"B" * 36)

    findings = scan_entries(
        (
            ("credentials/local.json", b"{}"),
            ("src/config.py", token),
            ("src/safe.py", b"PUBLIC_SETTING = 'safe'"),
        )
    )

    assert findings == (
        Finding(path="credentials/local.json", reason="forbidden sensitive path"),
        Finding(path="src/config.py", reason="sensitive content: GitHub token"),
    )
    assert token.decode() not in repr(findings)
