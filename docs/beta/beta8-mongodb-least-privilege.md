# Beta 8 — Experimental MongoDB least privilege

The matrix below describes roles created only inside a random Beta 8 scratch database on a verified MongoDB 7 replica set. Passwords are generated during the run and not written to manifests or output. MongoDB privileges are scoped to collection names; they cannot enforce a predicate such as a particular `_id`, track, revision, or state.

| Identity | Responsibility | Read | Insert | Update | Delete / admin | Status |
|---|---|---|---|---|---|---|
| `beta8-root` | Provisioner harness bootstrap and marker-verified cleanup | Scratch DB administration | Scratch DB provisioning | Scratch DB role provisioning | Temporary root in ephemeral container only | EXPERIMENTALLY_VERIFIED; used only by the isolated harness process and never by the runtime/preparation/editorial Mongo clients |
| `beta8-runtime` | Common read-only learner/runtime sample | Synthetic blocks and experimental generation projection | None | None | None | EXPERIMENTALLY_VERIFIED; MongoDB rejects direct editorial and publication writes |
| `beta8-preparer` | Stage synthetic batches | Beta 8 stage collections | Stage records/batches | Stage records/batches | None | EXPERIMENTALLY_VERIFIED; cannot edit blocks or generation heads |
| `beta8-editorial-authority` | C8/C10/C12 synthetic transaction participant | Exact C8/C12, block, and Beta 8 state collections | C8/C12, audit, immutable experimental generation | C8/C12, block, experimental head | No remove, dropDatabase, role/user administration or operational publication collection | EXPERIMENTALLY_VERIFIED for tested operations; protocol relies on trusted authority code |
| `beta8-audit` | Proposed future separate audit reader | Audit-only collections | None | None | None | PROPOSED; not separately exercised because mandatory audit shares transaction/client |

## Scope interpretation

MongoDB enforcement prevents the common runtime and preparation identities from directly altering the tested editorial collections. The authority identity needs collection-level write privilege for the participant transaction. Any code with that credential could bypass C8/C10 and write those collections directly; the database cannot distinguish a protocol call from a raw command by the same principal. This is the residual trust boundary and prevents a global-containment claim.

The Beta 8 authority role has no privilege on operational publication collections such as `activity_publications` or `track_publications`. Its test database is random and disposable; no role or credential is created outside it. The role proposal is not an operational migration plan until ownership, secret injection, process topology, collection inventory, rotation, revocation and rollout are verified under ADR-008.
