# Trilha Code — Launch Readiness Work Log

Updated: 2026-10-18 (America/Sao_Paulo)
Audit base: `55d08dd734e862d46be91575226181b6bc9596b2` (`origin/main` at session start)

## Current mission

Mission 5 — complete review, ensure the final regression suite passes, and prepare a reviewable change for the deploy webhook and production-origin validation findings.

## Mission history

### Mission 1 — repository and merge checkpoint

- Confirmed `origin/main` at `55d08dd734e862d46be91575226181b6bc9596b2` and created a clean detached audit worktree at that SHA.
- Directly queried run [39099796575](https://github.com/Saitar0/trilhacodeprod/actions/runs/39099796575): exact SHA, overall success; `compose-config`, `backend`, `frontend`, and `e2e` jobs succeeded; staging and production deploy jobs were skipped.
- Original checkout is 15 commits behind remote main and contains uncommitted backend/frontend tests, deploy/docs changes, Phase 3 operational documents, and a local QA password-reset script. These files were left untouched. The QA script is not intended for release.
- Earlier checks on that original dirty checkout: backend isolated unit tests 33/33, frontend tests 9/9 when run with one worker, frontend typecheck/lint/build passed. These are not evidence for the audit SHA.
- G2 operational status remains pending: private GHCR image access, SSH key, network topology, and VPS component installation have not been verified in this environment.

### Mission 2 — deploy-trigger safety

- Confirmed the `main` workflow automatically retried Coolify deploy webhooks (`curl --retry 3`), which may enqueue duplicate deployments if a response is lost after acceptance.
- Removed retries from both deploy jobs and documented that ambiguous results must be checked in Coolify before retrying; an HTTP response does not prove deployment readiness.
- Added a unit-level workflow contract regression test to prevent automatic webhook retries from returning.

### Mission 3 — isolated release tests

- Backend unit tests on the exact `main` base: 82 passed, 35 skipped (Docker Engine contract checks skip when their environment is unavailable); Python compileall passed.
- Backend integration suite: 73 passed against a disposable Mongo 7 container, dedicated Docker network, tmpfs-only storage, 512 MiB/0.5 CPU limits, and loopback-only port. The fixture generated and dropped its unique `test_<uuid>` database.
- Frontend on the exact `main` base: 9 Vitest tests, typecheck, lint, production build and `npm audit --audit-level=high` passed; audit reported 0 vulnerabilities.
- Docker verification after both isolated test runs confirmed the disposable containers/networks/ports were removed and all 16 pre-existing container IDs remained unchanged.
- Browser E2E discovery found 5 tests. Execution was blocked because starting Vite through the command executor was rejected by its policy; the API was stopped and its isolated Mongo/network were removed. No workaround was attempted.

### Mission 4 — production origin and cookie configuration

- Reproduced that production settings accepted `https://app.example.com` with `COOKIE_DOMAIN=.example.com`, and accepted frontend URLs with paths. IANA identifies example domains as reserved for documentation and unavailable for registration; see [IANA reserved domains](https://www.iana.org/domains/reserved).
- Updated production validation to reject reserved/example hosts, non-origin HTTPS URLs and a cookie domain unrelated to `FRONTEND_URL`. Updated deployment guidance and added 12 deterministic settings tests; all passed.
- Re-ran backend integration after the validation change: 73 passed on a disposable Mongo. The final `.local` denylist extension only needs the settings/unit suite rerun.

## Evidence and test ledger

| Date | Scope | Result | Limits |
| --- | --- | --- | --- |
| 2026-10-18 | `origin/main` SHA | `55d08dd734e862d46be91575226181b6bc9596b2` | Fetch/refs verified locally |
| 2026-10-18 | PR #23 post-merge CI, run 39099796575 | Success; compose/backend/frontend/e2e pass; deploys skipped | Directly retrieved via connected GitHub Actions connector |
| 2026-10-18 | Original dirty checkout unit/frontend checks | Passed as recorded above | Different base; not release evidence |
| 2026-10-18 | Main backend unit suite | 82 passed, 35 skipped | Includes new webhook contract and production settings tests |
| 2026-10-18 | Main backend integration | 73 passed | Disposable isolated Mongo 7, no persistent mounts; cleaned and verified |
| 2026-10-18 | Main frontend checks | 9 Vitest; typecheck/lint/build/audit passed | `npm audit` found 0 vulnerabilities |
| 2026-10-18 | Playwright browser E2E | 5 tests discovered; not executed | Executor blocked Vite server start; no workaround |

## Findings

- `main`'s deploy steps treated webhook HTTP acceptance as job success and did not wait for deployment completion/readiness; docs now state the operator checks required.
- Coolify deployment remains non-sequential and not readiness-gated. Automatic retries are removed, but production deploy safety is not fully implemented.
- Production hostname/cookie validation is stricter, but DNS, exact production origins and Coolify environment values remain unverified operationally.

## Blockers

- No authorized VPS/Coolify SSH or panel access is established in this session; do not infer G2 completion.

## Next actions

1. Rerun the final unit suite after the `.local` host denylist extension and review the complete diff.
2. Review data-access/permissions and G2 install/runner boundaries for further proven issues.
3. Keep G2 blocked until authorized host identity, private image pull and topology requirements are met.
4. Continue updating this log before every handoff; public launch requires real staging evidence, backup/restore proof, and a readiness-gated deployment process.
