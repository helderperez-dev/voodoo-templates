"""Create a deterministic CycloneDX file-component SBOM for templates."""

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
    excluded = {
        ".git", ".venv", ".pytest_cache", ".ruff_cache", ".mypy_cache",
        "__pycache__", ".voodoo", "target", "dist",
    }
    components = []
    for path in sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and not any(part in excluded or part.endswith(".egg-info") for part in path.parts)
        and path != args.output
    ):
        components.append(
            {
                "type": "file",
                "name": path.relative_to(root).as_posix(),
                "version": "1",
                "hashes": [
                    {"alg": "SHA-256", "content": hashlib.sha256(path.read_bytes()).hexdigest()}
                ],
            }
        )
    args.output.write_text(
        json.dumps(
            {"bomFormat": "CycloneDX", "specVersion": "1.5", "version": 1, "components": components},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(components)} template SBOM components")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
