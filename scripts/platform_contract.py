"""Cross-platform generated-template import and Store contract."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from voodoo.ui import Button
from voodoo.ui.styles.theme import default_theme


def main() -> int:
    rendered = Button("Platform", render_key="platform-contract").render()
    assert 'type="button"' in rendered
    assert 'id="vd-button-' in rendered
    assert "--vd-space-sm" in default_theme.to_css_variables()

    from voodoo_store import Store

    with tempfile.TemporaryDirectory(prefix="voodoo-template-") as directory:
        path = Path(directory) / "Generated App Ω" / "application.vstore"
        path.parent.mkdir()
        with Store.open(path) as store:
            store.put(b"platform:key", b"value")
        with Store.open(path) as reopened:
            assert reopened.get(b"platform:key") == b"value"
        writer = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "from voodoo_store import Store; "
                    "from pathlib import Path; import sys; "
                    "p=Path(sys.argv[1]); "
                    "exec(\"with Store.open(p) as s: s.put(b'process:key', b'process-value')\")"
                ),
                str(path),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert writer.returncode == 0, writer.stderr
        with Store.open(path) as process_reopened:
            assert process_reopened.get(b"process:key") == b"process-value"
    print("template platform contract passed (UI + Store reopen + process boundary)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
