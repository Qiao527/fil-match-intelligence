# Verification — public application

## Scope

This repository contains only the public application, self-authored fictional fixtures and necessary
pure computation/scoring primitives. No provider-acquisition adapters, private research modules,
real event files, reports, model weights or credentials are included. Runtime uses only Python's
standard library; development dependencies are version-pinned and locked in `uv.lock`.

## Executed checks

- Ruff: PASS.
- Public regression suite: 14 tests pass. These are this repository's tests; the private research
  project's larger suite is not claimed as this public repository's coverage.
- Fifteen fictional match/filter reports match frozen original-engine report hashes exactly.
- Separate Fraction arithmetic checks reproduce source sums and all sequence complements.
- Real Chromium: three matches, live API, action/JSON drilldown, full baseline, stale-state removal,
  no-Shot abstention and 390px responsiveness pass; no JavaScript page errors.
- Standard-library-only isolated interpreter can run the live analysis without the private package.
- Synthetic screenshots in this repository are captures of the running application, not app content.

The public engine deliberately shares measurement semantics with the original prototype but does
not distribute its research corpus or historical Git branches. Public Git history starts here.

## Limits

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
