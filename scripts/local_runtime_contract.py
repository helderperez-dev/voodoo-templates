"""Run the generated-app lifecycle contract against an isolated template copy."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).parents[1]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="voodoo-template-runtime-") as directory:
        project = Path(directory) / "default"
        shutil.copytree(ROOT / "default", project)
        result = subprocess.run(
            [
                sys.executable,
                "scripts/generated_app_contract.py",
                "--project",
                str(project),
            ],
            cwd=ROOT,
            check=False,
        )
        if result.returncode:
            return result.returncode
    print("template runtime contract passed (isolated generated-app lifecycle)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
