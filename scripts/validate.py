"""Validate the supported default template without importing Voodoo."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[1] / "default"
REQUIRED = (
    Path("app/page.py"),
    Path("pyproject.toml"),
    Path("voodoo.toml"),
    Path("README.md"),
    Path(".env.example"),
    Path("tests/test_app.py"),
    Path("tests/test_compatibility.py"),
    Path("tests/browser/test_app_browser.py"),
    Path(".github/workflows/quality.yml"),
    Path("COMPATIBILITY.json"),
)


def main() -> None:
    missing = [str(path) for path in REQUIRED if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit(f"missing template files: {', '.join(missing)}")
    pyproject = (ROOT / "pyproject.toml").read_text()
    if 'voodoo-framework>=3.2,<3.3' not in pyproject:
        raise SystemExit("default template must target the supported 3.2.x line")
    if 'requires-python = ">=3.12"' not in pyproject:
        raise SystemExit("default template must target Python 3.12 or newer")
    compatibility = json.loads((ROOT / "COMPATIBILITY.json").read_text())
    if compatibility.get("schema_version") != 1:
        raise SystemExit("template compatibility schema must be version 1")
    if compatibility.get("framework") != ">=3.2,<3.3":
        raise SystemExit("template compatibility must target Framework 3.2.x")
    if compatibility.get("store") != ">=0.3,<0.4":
        raise SystemExit("template compatibility must target Store 0.3.x")
    if compatibility.get("python") != ">=3.12":
        raise SystemExit("template compatibility must require Python 3.12+")
    for source in ROOT.glob("app/**/*.py"):
        compile(source.read_text(), str(source), "exec")
    if "[project.optional-dependencies]" not in pyproject:
        raise SystemExit("default template must expose optional development tools")
    quality = (ROOT / ".github/workflows/quality.yml").read_text()
    for command in ("ruff check", "mypy app", "pytest -q", "playwright install"):
        if command not in quality:
            raise SystemExit(f"starter quality workflow is missing: {command}")
    print("default template validation passed")


if __name__ == "__main__":
    main()
