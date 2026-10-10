"""Check that the published template and Framework scaffold share one contract.

The repositories intentionally keep different landing-page content, but they
must agree on the supported Framework line, routing entry points, and the
minimum files a generated application needs to start.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_TEMPLATE = (
    Path("app/page.py"),
    Path("pyproject.toml"),
    Path("voodoo.toml"),
    Path("README.md"),
    Path(".env.example"),
    Path("COMPATIBILITY.json"),
    Path("SOURCE_OF_TRUTH.json"),
)
REQUIRED_FRAMEWORK = REQUIRED_TEMPLATE + (
    Path("app/about/page.py"),
    Path("app/users/[id]/page.py"),
    Path("README.md"),
)
SUPPORTED_RANGE = 'voodoo-framework>=3.2,<3.3'


def _assert_files(root: Path, required: tuple[Path, ...], label: str) -> None:
    missing = [str(path) for path in required if not (root / path).is_file()]
    if missing:
        raise SystemExit(f"{label} is missing: {', '.join(missing)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--framework-root",
        type=Path,
        help="Framework checkout (defaults to a sibling ../voodoo checkout)",
    )
    args = parser.parse_args()

    template_root = Path(__file__).parents[1] / "default"
    _assert_files(template_root, REQUIRED_TEMPLATE, "default template")
    template_pyproject = (template_root / "pyproject.toml").read_text()
    if SUPPORTED_RANGE not in template_pyproject:
        raise SystemExit(f"default template must target {SUPPORTED_RANGE}")
    if 'requires-python = ">=3.12"' not in template_pyproject:
        raise SystemExit("default template must target Python 3.12 or newer")
    compatibility = json.loads((template_root / "COMPATIBILITY.json").read_text())
    if compatibility.get("framework") != ">=3.2,<3.3" or compatibility.get("store") != ">=0.3,<0.4":
        raise SystemExit("template compatibility metadata is outside the supported release ranges")
    for source in (template_root / "app").rglob("*.py"):
        compile(source.read_text(), str(source), "exec")

    framework_root = args.framework_root
    if framework_root is None:
        framework_root = template_root.parents[1] / "voodoo" / "src" / "voodoo" / "scaffold" / "default"
    _assert_files(framework_root, REQUIRED_FRAMEWORK, "Framework scaffold")
    framework_pyproject = (framework_root / "pyproject.toml").read_text()
    if SUPPORTED_RANGE not in framework_pyproject:
        raise SystemExit(f"Framework scaffold must target {SUPPORTED_RANGE}")
    if 'requires-python = ">=3.12"' not in framework_pyproject:
        raise SystemExit("Framework scaffold must target Python 3.12 or newer")
    for source in (framework_root / "app").rglob("*.py"):
        compile(source.read_text(), str(source), "exec")
    print("template/framework parity passed")


if __name__ == "__main__":
    main()
