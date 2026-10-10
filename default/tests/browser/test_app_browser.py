"""Minimal browser/a11y contract for the generated landing page."""

from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright


def _start_local_server_if_needed() -> subprocess.Popen[bytes] | None:
    """Provide a standalone local test server without masking configured URLs."""
    if os.environ.get("VOODOO_APP_URL"):
        return None
    url = "http://127.0.0.1:8766/"
    try:
        with urllib.request.urlopen(url, timeout=1) as response:
            if response.status == 200:
                return None
    except (OSError, urllib.error.URLError):
        pass
    project = Path(__file__).resolve().parents[2]
    log = project / ".browser-contract.log"
    handle = log.open("wb")
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "voodoo.core:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8766",
        ],
        cwd=project,
        env={
            **os.environ,
            "VOODOO_ENV": "test",
            "VOODOO_SECRET_KEY": "ci-generated-app-secret-key",
            "VOODOO_HOST": "127.0.0.1",
            "VOODOO_PORT": "8766",
        },
        stdout=handle,
        stderr=subprocess.STDOUT,
    )
    handle.close()
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if process.poll() is not None:
            break
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return process
        except (OSError, urllib.error.URLError):
            time.sleep(0.25)
    detail = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    process.terminate()
    process.wait(timeout=10)
    log.unlink(missing_ok=True)
    raise RuntimeError(f"generated app did not become ready: {detail}")


def test_landing_page_browser_contract() -> None:
    url = os.environ.get("VOODOO_APP_URL", "http://127.0.0.1:8766/")
    server = _start_local_server_if_needed()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": 1280, "height": 800})
                page.goto(url, wait_until="networkidle")
                assert page.locator("main").count() == 1
                assert page.locator("h1").first.inner_text()
                assert page.locator("body").inner_text().find("Your application") >= 0
            finally:
                browser.close()
    finally:
        if server is not None:
            server.terminate()
            server.wait(timeout=10)
            (Path(__file__).resolve().parents[2] / ".browser-contract.log").unlink(
                missing_ok=True
            )
