"""Live browser acceptance for the synthetic-only application."""

import argparse
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url")
    args = parser.parse_args()
    server = None
    url = args.url or "http://127.0.0.1:8652"
    if not url.startswith(("https://", "http://127.0.0.1:")):
        parser.error("HTTPS or local loopback required")
    try:
        if not args.url:
            server = subprocess.Popen(
                [sys.executable, "serve.py", "--port", "8652"], cwd=ROOT, stdout=subprocess.DEVNULL
            )
            for _ in range(100):
                try:
                    with urllib.request.urlopen(url + "/api/health", timeout=1) as r:
                        if r.status == 200:
                            break
                except OSError:
                    time.sleep(0.1)
            else:
                raise RuntimeError("Local service did not start")
        with sync_playwright() as p:
            executable = os.environ.get("FIL_CHROMIUM_PATH")
            browser = p.chromium.launch(**({"executable_path": executable} if executable else {}))
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(url)
            page.get_by_role("button", name="Run analysis").click()
            expect(page.locator(".card")).to_have_count(3)
            page.get_by_role("button", name="Inspect original actions").first.click()
            expect(page.locator("#raw")).to_contain_text("demo-1-action")
            page.get_by_role("button", name="Baseline & limits", exact=True).click()
            expect(page.locator("#units tr")).not_to_have_count(0)
            page.locator("#match").select_option("demo-3")
            expect(page.locator("#result")).to_be_hidden()
            page.get_by_role("button", name="Run analysis").click()
            expect(page.locator(".card")).to_have_count(3)
            page.locator("#period").select_option("2")
            expect(page.locator("#cards")).to_contain_text("No recorded Shots")
            page.locator("#match").select_option("demo-2")
            page.get_by_role("button", name="Run analysis").click()
            expect(page.locator(".card")).to_have_count(3)
            Path("artifacts").mkdir(exist_ok=True)
            page.screenshot(path="artifacts/desktop.png", full_page=True)
            page.set_viewport_size({"width": 390, "height": 844})
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            page.screenshot(path="artifacts/mobile.png", full_page=True)
            assert page.request.get(url + "/api/analyze?match=8658").status == 400
            assert not errors, errors
            browser.close()
        print(
            "PASS: API, three fixtures, drilldown, baseline, stale state, empty state, mobile"
        )
    finally:
        if server:
            server.terminate()
            server.wait(timeout=10)


if __name__ == "__main__":
    main()
