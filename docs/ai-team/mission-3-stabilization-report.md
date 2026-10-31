# Mission 3 — Beta 6.1 stabilization and consolidation

## Scope decision

PR #40 is broad because its head contains a 69-commit historical line from
`22dca645` through `c486fa7f`, including Beta 2–5 curriculum work and the
editorial-generation experiments, before the final foundation merge. Those
commits are inherited history, not new Beta 6.1 implementation.

The replacement branch is based on PR #39 and ports only the functional
learning chain required by Beta 6.1:

- session revocation, progress/import reliability, and foundation QA fixes;
- versioned activities and published-content readers;
- phase-owned MongoDB isolation;
- learner submission, reviewer scope, grading, and progress;
- HTTP/Chromium harness and synthetic fixture;
- Beta 6.1 CI validation and Mongo host-resolution fix.

Editorial generation protocols, writer containment, ADR-008 evidence, and
curriculum conversion experiments are intentionally excluded.

## Evidence

Replacement branch: `codex/beta6-1-http-chromium-clean-pr39`

- Base: `codex/beta5-contracts-integration-wave1`
- Local HTTP journey: 1 passed
- Local Chromium journey: 1 passed
- Frontend: typecheck, lint, and 29 tests passed
- Targeted backend contracts: 47 passed
- Diff against PR #39: 105 files; no editorial-generation tree

## Historical QA findings

The seven curriculum-fidelity failures are provenance failures: the fixture is
LF-normalized while the manifest expects the approved CRLF byte hash. The
hash gate must not be weakened. A separate provenance decision is required to
restore CRLF bytes or re-baseline all manifests consistently.

The G2 Docker failure is an environment prerequisite: the local daemon lacks
`mongo:7` while the test uses `--pull never`. CI must provision the pinned
image before running the contract; isolation assertions remain unchanged.

## Functional readiness snapshot

| Capability | State |
|---|---|
| Authentication and sessions | Implemented, targeted validation |
| Courses and learning reader | Partial; curriculum migration is not operational |
| Quiz, exercises, submissions, grading, progress | Implemented in Beta 6.1 slice, isolated validation |
| Admin flows | Implemented, broader integration validation pending |
| Premium subscriptions and entitlements | Absent |
| Code laboratory | Absent |
| AI tutor | Absent |
| Projects | Branch-only / staging contracts |
| Gamification | Absent |
| General notifications and support | Partial/absent |
| Editorial IAM and writers | Experimental and blocked |
| Production observability | Partial; operational validation pending |

## Remaining gates

Human review and the dependency chain `main → #38 → #39 → replacement PR`
remain required. No merge, deploy, staging activation, canonical curriculum
publication, writer activation, or ADR-008 unlock is authorized by this
report.
