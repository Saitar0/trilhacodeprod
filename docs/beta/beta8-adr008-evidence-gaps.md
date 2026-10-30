# Beta 8 — ADR-008 evidence gaps

ADR-008 remains BLOCKED. The isolated Beta 8 run cannot establish an operational baseline. From the local code and prior decisions, the following still require authorized operational evidence:

| Evidence area | State | Required evidence |
|---|---|---|
| Runtime identity per API, worker, CLI, seed and migration | REQUIRES_OPERATIONAL_CONFIRMATION | Process-to-credential ownership map and deployed configuration evidence |
| Effective MongoDB users/roles | UNKNOWN | Read-only authorized export of effective roles and collection privileges, including inherited roles |
| Credential source, rotation and revocation | UNKNOWN | Approved secret-management source and rotation/revocation evidence; no secret values |
| Writer call graph and external executors | NOT_VERIFIED | Runtime inventory covering routes, jobs, shells, scheduled tasks and operator paths |
| Replica-set/topology and transaction capabilities | NOT_VERIFIED | Authorized topology/session/majority/transaction evidence from target environment |
| IAM grant and policy-version authority | BLOCKED | Approved schema, ownership, version transition, revocation and authorization linearization semantics |
| Full writer containment | BLOCKED | Each W-01–W-16 integrated or technically denied; old identity bypass probes rejected |
| Snapshots, publication readers and generation pinning | BLOCKED | Source-revision consistency, immutable generations, reader behavior and rollback rehearsal |
| Student data preservation | REQUIRES_POLICY_AND_RUNTIME_PROOF | Approved retention contract and tests across actual restore/delete/migration paths |
| Backup, restore, incident and rollback | UNKNOWN | Owner-approved runbooks and successful authorized rehearsal |
| Audit access, retention, integrity and monitoring | UNKNOWN | Effective readers/ACL, retention, alerting, key lifecycle and incident evidence |
| Observability and multi-instance rollout/drain | UNKNOWN | Evidence all routes/workers/old processes support the policy epoch before cutover |

No production/staging system, Coolify, GHCR, credential source, or live database was accessed. Example settings and code do not establish deployed behavior. Beta 8 intentionally leaves all historical gate states unchanged.
