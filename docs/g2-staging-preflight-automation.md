# G2 staging MongoDB preflight

G2 is a manual, read-only inspection gate. This repository change hardens the software path; it does **not** install or update the runner on the VPS, create Docker networks, change Environment settings, run G2, create indexes, or authorize G3/G4/deploy.

## Components and deployment boundary

- Workflow: `.github/workflows/g2-staging-preflight.yml`, manual `workflow_dispatch` only, and job-level guard for `refs/heads/main`.
- SSH request: exactly `trilhacode-g2-preflight`; `StrictHostKeyChecking=yes` and a dedicated key remain required.
- Host runner: `/usr/local/sbin/trilhacode-g2-preflight-run`; root-only and not caller-configurable.
- Expected result manifest: `/etc/trilhacode-g2/preflight-manifest-v1.json`, installed root-owned with mode `0600`.
- Backend command in the pinned image: `python -m backend.g2_preflight`. This validates target configuration before importing the module that creates the Mongo client.
- Required network: `trilhacode-g2-preflight-internal`, a Docker internal network with only the intended staging MongoDB service attached before the ephemeral preflight starts. Do not reuse the current shared staging/proxy network.

The current image digest in the host runner is a pin for the previously approved image. Before activation, build and publish a new image containing `backend/g2_preflight.py`, `backend/g2_protocol.py`, and the updated `backend/indexes.py`; verify its source revision and immutable digest, then update the host runner pin and deploy the runner/manifest/image as a separate, authorized operation. A PR or CI run does not deploy these components.

The host environment file must remain root-owned mode `0600` and contain exactly one each of `ENV=staging`, `DB_NAME=trilhacode_staging`, `MONGO_URL`, `G2_MONGO_EXPECTED_HOST`, `G2_MONGO_EXPECTED_PORT=27017`, and `G2_MONGO_EXPECTED_CONTAINER_ID`. `MONGO_URL` must explicitly include `directConnection=true`; omission is rejected so replica-set discovery cannot redirect the client to another advertised member. The host/container ID must be the full 64-character ID reviewed for the intended service; a recreated Mongo container intentionally fails closed until its new identity is reviewed. `G2_MONGO_EXPECTED_HOST` must be the independently verified Docker network alias of that exact container. The runner checks that the internal network has only that MongoDB container attached and that the alias is present. The URI validator requires the same host, port, and database. It rejects seed lists, `mongodb+srv`, topology discovery options, unexpected schemes, and malformed URIs before a connection is created. Credentials are never printed. Root and the Docker daemon can still inspect container configuration while it exists; this remains within the host trust boundary.

## Versioned result protocol

The backend emits one JSON object on stdout with `schema_version: 1`, `result: "COMPLETE"`, and a `checks` array. Each check has only a stable manifest `id` and a `status`. The root-owned manifest is independent of the backend result. The host runner accepts exactly one JSON document and requires an exact one-to-one match with the manifest: missing, extra, duplicate, unknown, or malformed checks fail closed. Finding details, document IDs, values, exception text, stdout, and stderr are not sent to GitHub Actions.

Statuses:

- `OK`: the expected index definition is present, or its duplicate scan found no duplicates.
- `AUSENTE`: the index or its collection is absent, so the corresponding duplicate scan could not be run. This is informational before G4 and never causes index creation.
- `CONFLITO`: an index with matching keys but incompatible definition exists; the preflight fails.
- `DUPLICATAS`: the read-only scan found duplicate key groups; the preflight fails.

Duplicate aggregation uses a bounded result and `maxTimeMS`. A server-side timeout or interrupted scan is an error, never a clean result. These aggregations can still read a large collection; a preflight timeout must be investigated and must not be retried automatically.

Safe failure categories and codes are emitted without driver/daemon messages: URI invalid (40), database authentication (41), database connection (42), semantic preflight rejection (43), preflight execution (44), malformed protocol (45), database operation timeout (46), Docker failure (125–127), wall timeout (124), killed process (137), interrupted execution (129/130/143), cleanup failure or unverified cleanup (74), already-running lock (75), and lock/host configuration mismatches (69/78). A complete report with conflicts or duplicates exits 43. Inconsistent report/exit status fails as protocol-invalid. Container cleanup must be confirmed before any result is reported as complete. Exit 137 is not enough to infer a timeout and remains a distinct killed-process category.

## Read-only and non-goals

The G2 entry point only lists collections/indexes and performs duplicate-detection aggregation. It does not call index creation, migrations, seeds, document writes, user administration, Coolify, or deployment commands. `AUSENTE` is not an instruction to run `ensure-indexes`.

The ephemeral container uses the pinned image digest, fixed network, no published ports or mounts, no Docker socket, non-root UID, read-only root filesystem, dropped capabilities, `no-new-privileges`, resource limits, a wall timeout, and disabled Docker log driver. A root-only `flock` serializes runner invocations, including calls outside GitHub Actions concurrency. Only the wrapper gets Docker access, through a root-owned, fixed-purpose path.

## Required checks before any separate activation approval

1. Review and merge this code through the normal PR process; do not run G2 from PR validation.
2. Build/publish the backend image from the reviewed main revision using the approved image workflow; inspect the workflow result, source revision and immutable digest. Update the VPS pin only in a separate approved deployment.
3. Deploy the new runner and manifest to the VPS using a separately reviewed root operation; verify file hashes, owners and modes read-only afterward.
4. Provision the dedicated internal network and connect only the verified staging MongoDB service and the ephemeral preflight. Check host-gateway and other host service paths in a disposable environment. No Coolify proxy, Dev Forge container, or other service may join this network.
5. Verify the exact environment-file shape and Mongo alias against Docker metadata without displaying the URI or credentials. Confirm the dedicated Mongo user has read-only permissions for the target database.
6. Prove the GitHub private key correspondence without SSH: derive and compare fingerprints offline from the owner's original key, or use a separately approved fingerprint-only workflow that makes no network connection.
7. Confirm Environment branch restriction and approval policy. Environment values must never be printed. The current workflow fails closed on refs other than main.
8. Run automated tests and isolation experiments only with disposable MongoDB/Docker resources. Do not use staging as a test fixture.
9. Obtain a separate explicit approval for one G2 dispatch. G2 approval does not authorize index creation, migration, backup, or deployment steps.

## Test contract

CI covers URI allow/deny cases, validation-before-import, manifest/report completeness, duplicate and conflict semantics, sanitized error categories, duplicate-scan time limits, and absence of write calls. The runner harness substitutes a Docker CLI test double to cover network/image/Docker failures, authentication and connection categories, timeout, signal interruption before/after cidfile creation, cleanup ownership, output canaries, and semantic rejection. Backend integration tests in CI use the existing disposable MongoDB service only; none targets staging. No G2 workflow is dispatched by these tests.

## Rollback

Software rollback is a reviewed revert PR. Host activation rollback is separate: stop using the new runner/image, restore the prior pinned runner/image/manifest as a coordinated compatible set, and remove the dedicated network only after confirming it is empty and the MongoDB configuration is restored. Any MongoDB recreation, Coolify change, host firewall change, or operation affecting shared infrastructure requires its own approved change plan and health checks. Do not alter Dev Forge resources.
