# Beta 8 — Writer inventory reconciliation

## Method and limits

Reconciled the versioned `backend/integration_tests/editorial_writer_inventory_c13.json` against the named files and Python symbols in the Beta 8 base. All 17 listed paths exist and all named function symbols were found; W-17 is a class (`EditorialGenerationsPoC`), not a function. This confirms the historical static inventory still points at code in this commit. It does not prove call-graph or runtime exhaustiveness: external jobs, operator scripts, deployed credentials, and unknown processes remain unverified.

Every W-01–W-17 entry retains `runtime=NOT_VERIFIED` from C13/C16. Beta 8 does not alter or activate any legacy writer. Its representative draft-edit participant is new, test-only code and does not call `services/blocks.py`.

## Reconciled writers

| ID | Versioned writer(s) | Collections / effect | C13 class | Beta 8 disposition |
|---|---|---|---|---|
| W-01 | `services/tracks.py`: create/update/reorder | `tracks`, `edit_history` | A | Requires adaptation to shared authority; not integrated |
| W-02 | `services/tracks.py`: delete cascade | Content plus learner progress, attempts, publications, versions | B | Block; learner-data retention and recovery policy required |
| W-03 | `services/tracks.py`: duplicate | Track/node/block structures and history | B | Requires source/destination grants and compound idempotency |
| W-04 | `services/tracks.py`: publish | Track, content, activity publications, snapshots/versions | B | Block pending immutable generation/head protocol and reader compatibility |
| W-05 | `services/nodes.py`: create/update/reorder | `nodes`, history; hierarchy and ordering | A | Requires same track authority and relation validation |
| W-06 | `services/nodes.py`: delete/duplicate/clone | Nodes, blocks, relations, progress/history | B | Delete blocked; duplicate needs complete compound protocol |
| W-07 | `services/blocks.py`: CRUD/order | `content_blocks`, history | A | Representative protocol proof is synthetic only; real service remains direct |
| W-08 | `services/relations.py`: CRUD | `relations`, `nodes`, history | A | Requires transactional source/target scope and cycle validation |
| W-09 | `services/taxonomy.py`: taxonomy/tag/block-type CRUD | Global catalogs plus cross-track updates | D | Separate global authority/versioning decision required |
| W-10 | `services/imports.py`: import/job/lease | Import jobs, tracks, tags, nodes, blocks, relations, versions, history | B | Block from cutover until coordinated staging/recovery/fence integration |
| W-11 | `services/versions.py`: restore/apply/resume | Multi-collection replacement; may touch learner data | B | Block pending batch fencing, recovery and student-history rules |
| W-12 | `backend/integrity.py`: snapshots/version/migration/reconcile | Editorial versions/snapshots and reconciliation | A | Must bind a single source revision and avoid learner-state mutation |
| W-13 | `backend/seed.py`: seed helpers | Users, tracks, nodes, blocks, catalogs | B | Requires explicit disposable target and separate identity |
| W-14 | `backend/manage.py`: command/migration/index entrypoint | Operation-specific; exact effects vary | B | Classify each mutating command and constrain identity/target |
| W-15 | `services/immutable_publications.py` | Publication preparation lifecycle | D | Lifecycle/call graph remains unresolved |
| W-16 | `backend/audit.py::audit` | Functional audit records | A | Existing helper was not changed; real shared-session integration unverified |
| W-17 | `services/editorial_generations_poc.py::EditorialGenerationsPoC` | Dedicated PoC generation namespace | C | Retain experimental namespace; not evidence of runtime integration |

## Entry points and service identity

C13 records route, job, CLI, migration, and helper entrypoints. The codebase's active services use the shared database module; the actual identity/credential used by each deployed process cannot be inferred from source configuration or sample Compose files. The privilege matrix in `beta8-mongodb-least-privilege.md` is therefore a proposed experimental separation, not a claim about current deployments.

## Containment result

The persistent harness demonstrates that two restricted MongoDB identities cannot write `content_blocks` or Beta 8 generation heads, while the dedicated synthetic authority identity can complete the protocol participant. Because MongoDB roles are collection-scoped, a process holding the authority credential can still issue a direct update to `content_blocks`; this test suite explicitly preserves that limitation. Preventing a compromised/legacy authority process from bypassing protocol requires a separately controlled writer service/credential boundary, complete call-path containment, and operational role/secret verification. No global writer containment is claimed.
