# Verification — public application

## Scope

This repository contains only the public application, self-authored fictional fixtures and necessary
pure computation/scoring primitives. No provider-acquisition adapters, private research modules,
real event files, reports, model weights or credentials are included. Runtime uses only Python's
standard library; development dependencies are version-pinned and locked in `uv.lock`.

## Executed checks

- Ruff: PASS.
- Public regression suite: 16 tests pass. These are this repository's tests; the private research
  project's larger suite is not claimed as this public repository's coverage.
- Fifteen fictional match/filter reports match frozen original-engine report hashes exactly.
- Separate Fraction arithmetic checks reproduce source sums and all sequence complements.
- Real Chromium: three matches, live API, action/JSON drilldown, full baseline, stale-state removal,
  no-Shot abstention and 390px responsiveness pass; no JavaScript page errors.
- Standard-library-only isolated interpreter can run the live analysis without the private package.
- Synthetic screenshots in this repository are captures of the running application, not app content.

The public engine deliberately shares measurement semantics with the original prototype but does
not distribute its research corpus or historical Git branches. Public Git history starts here.

## Production acceptance status — 2026-10-27

Vercel production deployment `dpl_HwosNWmab62QceMQEwmmrkDuwhwn` reached **READY** for
commit `a3196039ec2ebdfba8d8259f625fd4e6ca7b9e26`, with the production alias
https://fil-match-intelligence.vercel.app. The application CI passed for that exact commit:
https://github.com/Qiao527/fil-match-intelligence/actions/runs/40537787858.

This is build evidence, **not completed online acceptance**. The managed execution environment
denies outbound access to the production hostname, and the Vercel authenticated-fetch tool lacks
its protection-bypass permission. No bypass was attempted. Anonymous API/browser verification
therefore remains pending the environment administrator's hostname allowlist update. Preview
authentication stays enabled; production authentication is disabled by project configuration.

The browser checker now compares 15 actual HTTP reports against the retained original-engine
hashes as well as checking health, catalog and the user journey. The same checker can be run
against the production URL once network access is permitted; local results are not represented
as production results.

Run `40538219580` passed lint and 14 tests but reached the ten-minute job timeout while
Ubuntu's Azure mirror downloaded optional font packages during `playwright install --with-deps`.
The browser journey did not run; that run is not a pass. The Ubuntu 24.04 runner already had
the browser's required shared libraries, as its installation log records. CI now installs the
pinned Playwright Chromium without repeating apt font installation. The complete browser
journey remains required and will fail if a necessary runtime library is absent.

## Scientific and measurement limits

No human usefulness evaluation, independent football confirmation, ratings, model fitting or
superior-to-human discovery. Fictional shot weights are illustrative, not calibrated xG.
The public web runtime has not received the previous Streamlit app's cold-start benchmark;
those timings must not be reused for this frontend. Hosted CI and deployment status are reported
separately from local results. Browser automation is not human acceptance or a security audit.

## Commit identity

New repository commits use author and committer `Qiao527` with GitHub's ID-based noreply address
`233347586+Qiao527@users.noreply.github.com`. No old private commits are copied or rewritten.

## Initial hosted regression and correction

The first hosted run passed lint and all 14 API/engine tests, but its browser check
exposed a real request/filter race: changing selection before the first response could
leave a report inconsistent with the visible filter. The client now tracks whether
analysis has started independently of whether response data exists. A browser regression
holds the stale full-match request and verifies the newer filtered request completes
with the no-Shot result. Failed initial CI is retained in Git history.

## Development dependency advisory

The public GitHub Advisory Database identifies `GHSA-6w46-j5rx-g56g` (pytest temporary-directory
handling) in pytest versions below 9.0.3. Both the pinned development declaration and lockfile were
updated to pytest 9.0.3. Lint, all 14 tests and the browser flow pass after the update. A fresh public
advisory query for pytest 9.0.3 returned no matches. This is a scoped advisory check, not a complete
security audit or a claim that no future vulnerability can exist. Production has no third-party
Python runtime dependencies. The advisory is https://github.com/advisories/GHSA-6w46-j5rx-g56g.

## Production catalog failure

The owner independently observed a platform 404 at `/api/matches` after the static page loaded.
This falsified any inference that a READY deployment meant the full product worked. Explicit
static/function build declarations and three API rewrites were added, with rewritten-path
regression coverage and a browser catalog-failure-state check. Local tests cannot certify
production routing; anonymous production acceptance must still be recorded separately.
