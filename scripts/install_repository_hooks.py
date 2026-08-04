"""Install the repository-owned Git hooks in the current checkout."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Configure only this checkout to use the versioned hook directory."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=ROOT,
        capture_output=True,
        check=True,
        text=True,
    )
    if Path(result.stdout.strip()).resolve() != ROOT:
        raise SystemExit("refusing to configure hooks outside the baseline checkout")
    subprocess.run(
        ["git", "config", "--local", "core.hooksPath", ".githooks"],
        cwd=ROOT,
        check=True,
    )
    print("Repository security hooks installed for this checkout.")


if __name__ == "__main__":
    main()
