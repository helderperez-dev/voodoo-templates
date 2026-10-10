"""Check (or explicitly synchronize) files owned by the canonical template."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

TEMPLATE_ROOT = Path(__file__).parents[1] / "default"
METADATA = TEMPLATE_ROOT / "SOURCE_OF_TRUTH.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--framework-root",
        type=Path,
        help="Framework scaffold directory (defaults to sibling checkout)",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Copy canonical shared files into the Framework scaffold",
    )
    args = parser.parse_args()
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    if metadata.get("schema_version") != 1:
        raise SystemExit("unsupported SOURCE_OF_TRUTH schema")
    files = tuple(Path(item) for item in metadata.get("shared_files", ()))
    if not files:
        raise SystemExit("SOURCE_OF_TRUTH.json must declare shared_files")
    framework_root = args.framework_root
    if framework_root is None:
        framework_root = TEMPLATE_ROOT.parents[1] / "voodoo" / "src" / "voodoo" / "scaffold" / "default"
    drift: list[str] = []
    for relative in files:
        source = TEMPLATE_ROOT / relative
        target = framework_root / relative
        if not source.is_file() or not target.is_file():
            drift.append(f"missing: {relative}")
            continue
        if source.read_bytes() != target.read_bytes():
            if args.sync:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
            else:
                drift.append(str(relative))
    if drift:
        raise SystemExit(
            "template/framework source drift detected: "
            + ", ".join(drift)
            + "; run scripts/check_source_sync.py --sync to update the mirror"
        )
    print(f"template source sync passed ({len(files)} shared files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
