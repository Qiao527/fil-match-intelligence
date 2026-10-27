"""Live browser acceptance for the synthetic-only application."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlencode

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url")
    args = parser.parse_args()
    server = None
    url = (args.url or "http://127.0.0.1:8652").rstrip("/")
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
            launch = {"executable_path": executable} if executable else {}
            # Preserve managed outbound policy for hosted acceptance. Local checks
            # remain loopback-only; never bypass the configured network proxy.
            proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
            if args.url and proxy:
                launch["proxy"] = {"server": proxy}
            browser = p.chromium.launch(**launch)
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            health = page.request.get(url + "/api/health")
            assert health.status == 200
            assert health.json() == {"status": "ok", "mode": "synthetic-only"}
            catalog = page.request.get(url + "/api/matches")
            assert catalog.status == 200
            assert {m["id"] for m in catalog.json()} == {"demo-1", "demo-2", "demo-3"}
            reference = json.loads((ROOT / "tests/fixtures/engine-reference.json").read_text())
            for case in reference["cases"]:
                query = urlencode({"match": case["match"], **case["selection"]})
                result = page.request.get(url + "/api/analyze?" + query)
                assert result.status == 200, query
                report = result.json()["report"]
                digest = hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest()
                assert digest == case["sha256"], query
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
            expect(page.locator("#result")).to_be_visible()
            expect(page.locator("#fixture")).to_contain_text("Beacon City")
            page.locator("#period").select_option("2")
            expect(page.locator("#cards")).to_contain_text("No recorded Shots")
            page.locator("#match").select_option("demo-2")
            page.get_by_role("button", name="Run analysis").click()
            expect(page.locator(".card")).to_have_count(3)
            # Hold a completed HTTP response in the browser, then release it after
            # a newer filtered response. This tests stale-response rejection without
            # leaving unfinished Playwright routing tasks at browser shutdown.
            page.evaluate("""() => {
              window.__originalFetch = window.fetch;
              window.fetch = async (...args) => {
                const res = await window.__originalFetch(...args);
                if (String(args[0]) === '/api/analyze?match=demo-3') {
                  const body = await res.arrayBuffer();
                  await new Promise(resolve => { window.__releaseStale = resolve; });
                  return new Response(body, {status: res.status, headers: res.headers});
                }
                return res;
              };
            }""")
            page.locator("#match").select_option("demo-3")
            page.get_by_role("button", name="Run analysis").click()
            page.wait_for_function("typeof window.__releaseStale === 'function'")
            page.locator("#period").select_option("2")
            expect(page.locator("#cards")).to_contain_text("No recorded Shots")
            expect(page.locator("#scope")).to_contain_text("Second half")
            page.evaluate("() => {window.__releaseStale(); window.fetch = window.__originalFetch;}")
            page.evaluate(
                "() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))"
            )
            expect(page.locator("#cards")).to_contain_text("No recorded Shots")
            page.locator("#match").select_option("demo-2")
            page.get_by_role("button", name="Run analysis").click()
            expect(page.locator("#result")).to_be_visible()
            expect(page.locator("#fixture")).to_contain_text("Atlas United")
            Path("artifacts").mkdir(exist_ok=True)
            page.screenshot(path="artifacts/desktop.png", full_page=True)
            page.set_viewport_size({"width": 390, "height": 844})
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            page.screenshot(path="artifacts/mobile.png", full_page=True)
            assert page.request.get(url + "/api/analyze?match=8658").status == 400
            assert not errors, errors
            browser.close()
        print("PASS: health, catalog, 15 HTTP report hashes, three fixtures, drilldown,")
        print("baseline, stale state, empty state, mobile; zero JavaScript page errors")
    finally:
        if server:
            server.terminate()
            server.wait(timeout=10)


if __name__ == "__main__":
    main()
