from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest

from scripts.bootstrap_template import DEFAULTS, apply_identity, iter_text_files, load_config


def write_config(path: Path, **overrides: str) -> dict[str, str]:
    config = {**DEFAULTS, **overrides}
    path.write_text(json.dumps(config), encoding="utf-8")
    return config


def test_load_config_accepts_documented_fields(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    expected = write_config(path, project_name="  Example Platform  ")
    expected["project_name"] = "Example Platform"
    assert load_config(path) == expected


@pytest.mark.parametrize(
    "mutation",
    [
        lambda config: config.pop("project_name"),
        lambda config: config.update(project_name=""),
        lambda config: config.update(python_package="Invalid-Package"),
    ],
)
def test_load_config_rejects_invalid_configuration(
    tmp_path: Path, mutation: Callable[[dict[str, str]], object]
) -> None:
    path = tmp_path / "config.json"
    config = dict(DEFAULTS)
    mutation(config)
    path.write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(path)


def test_apply_identity_renames_and_rewrites(tmp_path: Path) -> None:
    package = tmp_path / "gcp/services/control-plane/src/platform_api"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("platform_api APB", encoding="utf-8")
    github = tmp_path / ".github"
    github.mkdir()
    (github / "CODEOWNERS.example").write_text("* @YOUR-GITHUB-HANDLE", encoding="utf-8")
    config_path = tmp_path / "template.config.json"
    config = write_config(
        config_path,
        project_short_name="EXAMPLE",
        python_package="example_api",
        github_owner="example-owner",
    )

    assert apply_identity(tmp_path, config, config_path) == 3
    assert (tmp_path / "gcp/services/control-plane/src/example_api/__init__.py").read_text() == (
        "example_api EXAMPLE"
    )
    assert (github / "CODEOWNERS").read_text() == "* @example-owner"
    assert iter_text_files(tmp_path, {config_path})
