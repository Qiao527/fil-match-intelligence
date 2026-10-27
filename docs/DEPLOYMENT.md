# Deployment

## Owner setup

The connected Vercel service can list the intended team but returned HTTP 403 when creating a
project. There is no authenticated local CLI fallback. The repository owner therefore needs to:

1. Open https://vercel.com/new and select `qiao527's projects`.
2. Import `Qiao527/fil-match-intelligence` as project `fil-match-intelligence`.
3. Choose framework **Other**, repository root directory, and Deploy.

`vercel.json` supplies the `public` output directory and browser response headers. Python APIs
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
JavaScript syntax, 14 regression tests and a real Chromium user journey, including a deliberately
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
