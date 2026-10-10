"""Portable generated-app start, stop, restart, and Store persistence contract."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


def _wait_for_app(url: str, log_path: Path, process: subprocess.Popen[bytes]) -> None:
    deadline = time.monotonic() + 30
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        if process.poll() is not None:
            break
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                body = response.read()
                if response.status == 200 and b"Your application" in body:
                    health_url = url.rsplit("/", 1)[0] + "/healthz"
                    ready_url = url.rsplit("/", 1)[0] + "/readyz"
                    with urllib.request.urlopen(health_url, timeout=1) as health:
                        health_payload = json.loads(health.read())
                    with urllib.request.urlopen(ready_url, timeout=1) as ready:
                        ready_payload = json.loads(ready.read())
                    if (
                        health.status == 200
                        and health_payload.get("status") == "ok"
                        and ready.status == 200
                        and ready_payload.get("status") == "ready"
                    ):
                        return
                    last_error = RuntimeError(
                        "generated app probes did not report healthy status"
                    )
        except (OSError, ValueError) as error:
            last_error = error
        time.sleep(0.5)
    detail = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    raise RuntimeError(f"generated app did not become ready: {last_error}\n{detail}")


def _start(project: Path, port: int, log_path: Path) -> subprocess.Popen[bytes]:
    log = log_path.open("wb")
    environment = os.environ.copy()
    environment.update(
        {
            "VOODOO_ENV": "test",
            "VOODOO_SECRET_KEY": "ci-generated-app-secret-key",
            "VOODOO_HOST": "127.0.0.1",
            "VOODOO_PORT": str(port),
        }
    )
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "voodoo.core:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=project,
        env=environment,
        stdout=log,
        stderr=subprocess.STDOUT,
    )
    # The child owns the descriptor after spawn; close the parent handle.
    log.close()
    return process


def _stop(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)


def _browser_check(url: str) -> None:
    """Run the minimal generated-page browser contract when requested."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise RuntimeError("--browser requires the Playwright package") from error
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto(url, wait_until="networkidle")
        if page.locator("main").count() != 1:
            raise RuntimeError("generated app browser contract expected one <main>")
        if not page.locator("h1").first.inner_text():
            raise RuntimeError("generated app browser contract expected a heading")
        if "Your application" not in page.locator("body").inner_text():
            raise RuntimeError("generated app browser contract found unexpected page text")
        browser.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path("default"))
    parser.add_argument("--port", type=int, default=18766)
    parser.add_argument(
        "--browser",
        action="store_true",
        help="run the optional Chromium landing-page contract while the app is live",
    )
    args = parser.parse_args()
    project = args.project.resolve()
    if not project.is_dir():
        raise SystemExit(f"generated project does not exist: {project}")

    url = f"http://127.0.0.1:{args.port}/"
    log_path = project / ".generated-app-contract.log"
    first = _start(project, args.port, log_path)
    try:
        _wait_for_app(url, log_path, first)
        store = project / ".voodoo" / "application.vstore"
        if not store.is_file() or store.stat().st_size == 0:
            raise RuntimeError("generated app did not create a durable Store")
        if args.browser:
            _browser_check(url)
    finally:
        _stop(first)

    second = _start(project, args.port, log_path)
    try:
        _wait_for_app(url, log_path, second)
        if not store.is_file() or store.stat().st_size == 0:
            raise RuntimeError("generated Store did not survive restart")
    finally:
        _stop(second)
        log_path.unlink(missing_ok=True)

    print("generated app contract passed (start + stop + restart + Store persistence)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
