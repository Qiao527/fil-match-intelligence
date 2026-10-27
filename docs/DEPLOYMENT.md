# Deployment

## Owner setup

The connected Vercel service can list the intended team but returned HTTP 403 when creating a
project. There is no authenticated local CLI fallback. The repository owner therefore needs to:

1. Open https://vercel.com/new and select `qiao527's projects`.
2. Import `Qiao527/fil-match-intelligence` as project `fil-match-intelligence`.
3. Choose framework **Other**, repository root directory, and Deploy.

`vercel.json` explicitly builds `public` through the pinned static builder and declares three
separate pinned Python function builds, with `/api/health`, `/api/matches` and `/api/analyze`
rewritten to their function artifacts. It also supplies browser response headers. Python APIs
live under `api/`. No environment variables, credentials, provider files, paid database or new
model-training permission are required. Do not upload the private research checkout.

The configuration explicitly selects **Other** (`framework: null`), overriding Python framework
autodetection: this application serves static assets alongside individual Python API functions.
The first import of commit `72461a2` failed before dependency installation because Vercel's
uv 0.13.5 did not satisfy the project's exact uv 0.12.23 requirement. The supported tooling
range now accepts both versions; CI still pins uv 0.12.23, development dependencies remain
locked, and the production application has no third-party Python dependencies. Production
access is public; Vercel Authentication remains enabled for previews.

After import, the Git integration builds new pushes. The application CI also checks lint,
JavaScript syntax, 16 regression tests and a real Chromium user journey, including a deliberately
delayed stale HTTP response. Green checks and deployed behavior are separate evidence.

## Acceptance after a deployment exists

- Visit the production domain without logging into Vercel; a protected preview is not public access.
- `GET /api/health` returns HTTP 200 and `synthetic-only` mode.
- Load the match catalog and execute all three fictional fixtures.
- Test team/period filtering, source JSON, comparison actions and the complete baseline.
- Select Beacon–Westhaven's second half and confirm no-Shot abstention.
- Rapidly change filters and check the report agrees with the visible controls.
- Check 390px layout and browser console.
- Confirm a real-match request (`/api/analyze?match=8658`) returns HTTP 400.

The browser checker accepts an HTTPS deployment URL:

```bash
uv run --frozen python tests/browser_check.py --url https://YOUR-VERIFIED-PRODUCTION-DOMAIN
```

Do not paste Vercel access tokens into GitHub, the application, or chat. Production publishing is
synthetic-only; historical private PR merges and provider-data redistribution remain outside scope.

## Rollback

Use Vercel's deployment history to restore the last verified deployment. Inspect the current Git
commit and CI first. Preserve public Git history; do not force-push main to hide a failed release.

## Catalog 404 correction

A user request to `/api/matches` returned platform `404 NOT_FOUND` while static HTML loaded.
Previous local checks bypassed deployment routing and therefore could not establish that the
functions were deployed. Explicit builder entries and API rewrites replace reliance on static
output autodetection. The static build runs only JavaScript syntax validation; package.json has
no dependencies. The API accepts both original and rewritten function paths while retaining
strict query validation. A regression checks that every public API destination has a declared
function artifact; a browser regression verifies that catalog failure shows an unavailable
state instead of leaving a loading label. Production verification remains a separate gate.

Builder versions are pinned to Python 28.0.0 and static-build 24.0.0, whose declared
peer dependency matches Vercel CLI 65.1.0: `@vercel/build-utils` 15.0.0. The first explicit
build attempt used newer builders requiring 15.1.0 and failed dependency resolution; no
force/legacy-peer-deps override was used.

The next explicit build exposed `PYTHON_ENTRYPOINT_NOT_FOUND`: imported handler aliases
were not discoverable by the builder. All three API files now define top-level handler
subclasses with shared implementation. A regression checks discovery shape and callable
HTTP methods. Deployment `dpl_8FkCvyif5n5UvY3SZQgVgnWFXbT5` at commit `0ec45bb`
reached READY with those function builds. This does not substitute for anonymous endpoint
and browser acceptance; direct production access from the managed executor remains blocked.
