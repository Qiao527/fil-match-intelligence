"""Interleaved local browser comparison; not a production/server cold-start benchmark."""

import argparse
import hashlib
import io
import json
import os
import shutil
import statistics
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent", default="26a91dbc7db74c16ecd335d7f5faf6ca8566b92b")
    args = parser.parse_args()
    samples = []
    with tempfile.TemporaryDirectory(prefix="fil-spatial-perf-") as directory:
        base = Path(directory)
        parent = base / "parent"
        parent.mkdir()
        archive = subprocess.check_output(["git", "archive", args.parent], cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
            bundle.extractall(parent, filter="data")
        candidate = base / "candidate"
        candidate.mkdir()
        for name in ["public", "src", "api"]:
            shutil.copytree(
                ROOT / name, candidate / name, ignore=shutil.ignore_patterns("__pycache__")
            )
        shutil.copy2(ROOT / "serve.py", candidate / "serve.py")
        servers = []
        try:
            for name, port in [("parent", 8654), ("candidate", 8655)]:
                servers.append(
                    subprocess.Popen(
                        [sys.executable, "serve.py", "--port", str(port)],
                        cwd=base / name,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                )
                for _ in range(100):
                    try:
                        with urllib.request.urlopen(
                            f"http://127.0.0.1:{port}/api/health", timeout=1
                        ):
                            break
                    except OSError:
                        time.sleep(0.05)
                else:
                    raise RuntimeError("Local benchmark server did not start")
            with sync_playwright() as p:
                executable = os.environ.get("FIL_CHROMIUM_PATH")
                browser = p.chromium.launch(
                    **({"executable_path": executable} if executable else {})
                )
                for pair in range(10):
                    order = ["parent", "candidate"] if pair % 2 == 0 else ["candidate", "parent"]
                    for name in order:
                        context = browser.new_context(viewport={"width": 1440, "height": 1100})
                        page = context.new_page()
                        page.goto(f"http://127.0.0.1:{8654 if name == 'parent' else 8655}")
                        expect(page.locator("#run")).to_be_enabled()
                        page_ms = page.evaluate("performance.now()")
                        # Time inside the browser, ending at the DOM status update.
                        page.evaluate("""() => {window.__start = performance.now();
                            window.__done = null;
                            const observer = new MutationObserver(() => {
                              const text = document.querySelector('#status').textContent;
                              if (text.startsWith('Analysis complete')) {
                                window.__done = performance.now() - window.__start;
                                observer.disconnect();
                              }
                            });
                            observer.observe(document.querySelector('#status'), {childList:true});
                            document.querySelector('#run').click();
                        }""")
                        page.wait_for_function("window.__done !== null")
                        samples.append(
                            dict(
                                pair=pair,
                                variant=name,
                                page_ready_ms=page_ms,
                                analysis_dom_ms=page.evaluate("window.__done"),
                            )
                        )
                        context.close()
                browser.close()
        finally:
            for server in servers:
                server.terminate()
                server.wait(timeout=10)
        summary = {}
        for name in ["parent", "candidate"]:
            summary[name] = {}
            for metric in ["page_ready_ms", "analysis_dom_ms"]:
                values = [s[metric] for s in samples if s["variant"] == name]
                summary[name][metric] = dict(
                    median=statistics.median(values),
                    minimum=min(values),
                    maximum=max(values),
                    stdev=statistics.stdev(values),
                )
            summary[name]["asset_bytes"] = sum(
                f.stat().st_size for f in (base / name / "public").glob("*") if f.is_file()
            )
        result = dict(
            parent_commit=args.parent,
            candidate_asset_sha256={
                f.name: hashlib.sha256(f.read_bytes()).hexdigest()
                for f in (candidate / "public").glob("*") if f.is_file()
            },
            methodology=__doc__,
            repetitions=10,
            browser="Chromium, fresh context per sample, one shared process",
            fixture="demo-1, full match, both teams",
            samples=samples,
            summary=summary,
            limits=("Local loopback, small fictional fixtures; not production latency, "
                    "physical timing, or usefulness evidence."),
        )
        (ROOT / "artifacts").mkdir(exist_ok=True)
        (ROOT / "artifacts/spatial-performance.json").write_text(
            json.dumps(result, indent=2) + "\n"
        )
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
