# Trilha Code — Launch Readiness Work Log

Updated: 2026-10-18 (America/Sao_Paulo)
Audit base: `55d08dd734e862d46be91575226181b6bc9596b2` (`origin/main` at session start)

## Current mission

Mission 7 — verify the corrected PR #24 CI, continue public-access/security review, and keep staging/G2 readiness evidence current.

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

### Mission 5 — read-only Coolify inventory and staging cookie defaults

- Read-only team-scoped Coolify inventory confirmed the Trilha Code project currently has one API application and one MongoDB resource. The staging API is `exited:unhealthy`, has no container present, no registry image configured, health checking disabled, and no deployment history. The staging Mongo is `running:healthy` and private.
- Staging Mongo has no Coolify backup schedule. No backup/restore job was run.
- Listed environment key names only (never values): API keys include `ENV`, `DB_NAME`, `FRONTEND_URL`, `CORS_ORIGINS`, `MONGO_URL`, and `JWT_SECRET`; there is no `COOKIE_SECURE` key. No database env keys were returned. Settings previously defaulted secure cookies only in production, so staging would emit cookies without `Secure` unless manually configured.
- Changed runtime default to secure cookies for both staging and production, and make explicit `COOKIE_SECURE=false` a staging configuration error. Added two tests; final unit suite is 84 passed / 35 skipped. Python compileall, YAML parse, and whitespace checks passed.
- This is code-only; it does not change the live Coolify resource. A new backend image and reviewed deployment would be required before the staging behavior changes.

### Mission 6 — access-control review and CI lint repair

- Reviewed API route guards and service checks for tracks, nodes, progress, notes, reviews, and submissions. Public student reads filter to published public tracks/nodes and student-owned data; administrative mutations require role permissions. No concrete authorization bypass was reproduced in this pass.
- PR #24 CI run `39101340050` on merge SHA `da341f6a77af8a41c1ee25846b478d53d96bd038`: Compose, frontend (typecheck/lint/unit/build/dependency audit), E2E and 119 backend unit tests passed; Ruff failed on three import-order violations in changed files; downstream backend checks were skipped, and deploy jobs were skipped.
- Corrected only the three Ruff import-order findings. Local `ruff check backend` passed; local backend unit suite passed 84, with 35 Linux runner-only Docker contract tests skipped. No Mongo integration or deploy was run for this formatting-only correction.
- Browser E2E on CI passed all student and administrator scenarios against the disposable Mongo service, including student progress and submission, and administrator track editing/import/version comparison.

## Evidence and test ledger

| Date | Scope | Result | Limits |
| --- | --- | --- | --- |
| 2026-10-18 | `origin/main` SHA | `55d08dd734e862d46be91575226181b6bc9596b2` | Fetch/refs verified locally |
| 2026-10-18 | PR #23 post-merge CI, run 39099796575 | Success; compose/backend/frontend/e2e pass; deploys skipped | Directly retrieved via connected GitHub Actions connector |
| 2026-10-18 | Original dirty checkout unit/frontend checks | Passed as recorded above | Different base; not release evidence |
| 2026-10-18 | Main backend unit suite / PR branch revision | 84 passed, 35 skipped | Includes workflow, origin, and staging-cookie contracts |
| 2026-10-18 | Main backend integration | 73 passed | Disposable isolated Mongo 7, no persistent mounts; cleaned and verified |
| 2026-10-18 | Main frontend checks | 9 Vitest; typecheck/lint/build/audit passed | `npm audit` found 0 vulnerabilities |
| 2026-10-18 | Playwright browser E2E | 5 tests discovered; not executed | Executor blocked Vite server start; no workaround |
| 2026-10-18 | PR #24 CI run 39101340050 | Compose, frontend and E2E passed; 119 backend unit tests passed; Ruff failed | Exact failure was three import-order violations; remaining backend steps were skipped |
| 2026-10-18 | Ruff repair in PR #24 worktree | `ruff check backend` passed; backend unit suite 84 passed / 35 skipped | Changes only reorder imports; awaiting CI on corrected commit |

## Findings

- `main`'s deploy steps treated webhook HTTP acceptance as job success and did not wait for deployment completion/readiness; docs now state the operator checks required.
- Coolify deployment remains non-sequential and not readiness-gated. Automatic retries are removed, but production deploy safety is not fully implemented.
- Production hostname/cookie validation is stricter, but DNS, exact production origins and Coolify environment values remain unverified operationally.

## Blockers

- No SSH/Hostinger console access is established. Coolify access in this session is limited to team-scoped read-only metadata; do not infer G2 completion.
- Current read-only Coolify evidence: the Trilha Code staging API has no container, no registry image, disabled health checks, and zero deployments; the staging Mongo has no backup schedule.
- The local browser E2E could not start because the executor blocked the Vite server command; CI run 39101340050 passed the E2E job on PR #24, while backend CI failed only at Ruff and has been corrected locally.
- Actual environment values, SSH secrets/fingerprint, GHCR pull identity, and network memberships remain unverified; do not read or alter secrets to resolve this.

## Next actions

1. Push the Ruff-only correction and verify all PR #24 CI jobs on the new head.
2. Review data-access/permissions and G2 install/runner boundaries for further proven issues.
3. Keep G2 blocked until image, SSH identity, read-only Mongo account, dedicated network, backup/restore, and host runner requirements are met and separately approved.
4. Continue updating this log before every handoff; public launch requires real staging evidence, backup/restore proof, a healthy API, and a readiness-gated deployment process.
