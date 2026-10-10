"""Create a deterministic checksum manifest for the template bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).parents[1]
    files = [
        path
        for path in root.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and "__pycache__" not in path.parts
        and ".ruff_cache" not in path.parts
        and ".pytest_cache" not in path.parts
        and ".mypy_cache" not in path.parts
        and ".venv" not in path.parts
        and ".voodoo" not in path.parts
        and "target" not in path.parts
        and "dist" not in path.parts
        and path != args.output
    ]
    entries = [
        {
            "file": path.relative_to(root).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "bytes": path.stat().st_size,
        }
        for path in sorted(files)
    ]
    args.output.write_text(
        json.dumps({"manifest_version": 1, "artifacts": entries}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(entries)} template bundle checksums")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
