"""Audit installed Template-job dependencies without editable-app skips.

Generated projects are intentionally installed as the local ``voodoo-app``
package, which pip-audit cannot resolve from PyPI. Auditing the exact local
environment with ``--skip-editable`` keeps only that unpublished package out
while auditing every other installed distribution.
"""

from __future__ import annotations

import subprocess
import sys


def main() -> int:
    # --local audits the exact installed environment; --skip-editable excludes
    # only the generated, unpublished voodoo-app project while retaining every
    # published Framework/Store/runtime dependency.
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pip_audit",
            "--local",
            "--skip-editable",
            "--progress-spinner",
            "off",
        ],
        check=False,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
