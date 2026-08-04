"""Apply a validated project identity to a fresh baseline checkout."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Final

DEFAULTS: Final = {
    "project_name": "Agentic Platform Baseline",
    "project_short_name": "APB",
    "project_slug": "agentic-platform-baseline",
    "python_package": "platform_api",
    "python_distribution": "agentic-platform-control-plane",
    "typescript_scope": "@agentic-platform",
    "environment_prefix": "PLATFORM_",
    "firebase_emulator_project": "agentic-platform-local",
    "error_urn_namespace": "urn:agentic-platform",
    "github_owner": "YOUR-GITHUB-HANDLE",
}
SKIPPED_DIRECTORIES: Final = {".git", ".venv", "node_modules", ".next", ".local"}
TEXT_SUFFIXES: Final = {
    "",
    ".css",
    ".example",
    ".html",
    ".js",
    ".json",
    ".md",
    ".mjs",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}


def load_config(path: Path) -> dict[str, str]:
    """Load and validate the complete, secret-free template identity."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if set(raw) != set(DEFAULTS) or not all(isinstance(value, str) for value in raw.values()):
        raise ValueError("configuration must contain exactly the documented string fields")
    config = {key: value.strip() for key, value in raw.items()}
    if any(not value for value in config.values()):
        raise ValueError("configuration values cannot be empty")
    patterns = {
        "project_short_name": r"[A-Z][A-Z0-9]{1,11}",
        "project_slug": r"[a-z0-9]+(?:-[a-z0-9]+)*",
        "python_package": r"[a-z][a-z0-9_]*",
        "python_distribution": r"[a-z0-9]+(?:-[a-z0-9]+)*",
        "typescript_scope": r"@[a-z0-9]+(?:-[a-z0-9]+)*",
        "environment_prefix": r"[A-Z][A-Z0-9_]*_",
        "firebase_emulator_project": r"[a-z][a-z0-9-]{4,29}",
        "error_urn_namespace": r"urn:[a-z0-9][a-z0-9-]*",
        "github_owner": r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?",
    }
    invalid = [key for key, pattern in patterns.items() if not re.fullmatch(pattern, config[key])]
    if invalid:
        raise ValueError(f"invalid template values: {', '.join(invalid)}")
    return config


def iter_text_files(root: Path, excluded: set[Path]) -> list[Path]:
    """Return deterministic candidate text files without traversing generated content."""
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path not in excluded
        and not SKIPPED_DIRECTORIES.intersection(path.relative_to(root).parts)
        and path.suffix.lower() in TEXT_SUFFIXES
    )


def apply_identity(root: Path, config: dict[str, str], config_path: Path) -> int:
    """Rename the Python package and replace baseline identity tokens."""
    source_package = root / "gcp/services/control-plane/src" / DEFAULTS["python_package"]
    target_package = source_package.with_name(config["python_package"])
    if source_package.exists() and source_package != target_package:
        if target_package.exists():
            raise ValueError(f"target Python package already exists: {target_package}")
        source_package.rename(target_package)

    codeowners_example = root / ".github/CODEOWNERS.example"
    codeowners = root / ".github/CODEOWNERS"
    if codeowners_example.is_file() and not codeowners.exists():
        shutil.copyfile(codeowners_example, codeowners)

    replacements = {DEFAULTS[key]: config[key] for key in DEFAULTS if DEFAULTS[key] != config[key]}
    excluded = {
        config_path.resolve(),
        (root / "template.config.example.json").resolve(),
        Path(__file__).resolve(),
    }
    changed = 0
    for path in iter_text_files(root, excluded):
        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        updated = original
        for old, new in replacements.items():
            updated = updated.replace(old, new)
        if updated != original:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
    return changed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("template.config.json"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true", help="validate configuration only")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    config_path = args.config.resolve()
    if not (root / "pyproject.toml").is_file() or not (root / "frontend").is_dir():
        raise SystemExit("refusing to bootstrap outside an Agentic Platform Baseline checkout")
    try:
        config = load_config(config_path)
        changed = 0 if args.check else apply_identity(root, config, config_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"bootstrap failed: {exc}") from exc
    action = "validated" if args.check else f"applied to {changed} files"
    print(f"Template configuration {action}.")


if __name__ == "__main__":
    main()
