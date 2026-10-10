"""Compatibility and upgrade-preservation contract for generated projects."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_compatibility_metadata_matches_project_requirements() -> None:
    metadata = json.loads((ROOT / "COMPATIBILITY.json").read_text())
    pyproject = (ROOT / "pyproject.toml").read_text()

    assert metadata["schema_version"] == 1
    assert metadata["framework"] == ">=3.2,<3.3"
    assert metadata["store"] == ">=0.3,<0.4"
    assert metadata["python"] == ">=3.12"
    assert 'voodoo-framework>=3.2,<3.3' in pyproject
    assert 'requires-python = ">=3.12"' in pyproject


def test_upgrade_file_set_preserves_runtime_store(tmp_path: Path) -> None:
    """A template refresh must not include durable application state."""
    project = tmp_path / "app"
    project.mkdir()
    state = project / ".voodoo" / "application.vstore"
    state.parent.mkdir()
    state.write_bytes(b"durable-state")

    template_files = [
        path.relative_to(ROOT)
        for path in ROOT.rglob("*")
        if path.is_file() and ".voodoo" not in path.parts
    ]
    assert all(path.parts[:1] != (".voodoo",) for path in template_files)

    # The upgrade contract is preservation, not a destructive replacement.
    assert state.read_bytes() == b"durable-state"
