# Beta 8 — Experimental curriculum-promotion contract

## Scope

`ExperimentalPromotionCandidate` and `ExperimentalPromotionIntent` accept only records marked `BETA8_SYNTHETIC_ONLY`, a `beta8-track-synthetic-*` track identity, a validated synthetic batch, a canonical payload SHA-256, an exact contract version, a synthetic approval enum, and target namespace `beta8_experimental`. The service is not imported by active routes/startup and does not read the Beta 5 staging collections or the real revised curriculum.

An intent binds batch/hash, synthetic source revision, track, generation, operation ID, expected C8 revision, fence, state and preservation behavior. Reusing an operation ID with a changed payload is rejected by the shared C10 idempotency fingerprint. Unknown or invalid state fails closed.

## Experimental state transition

`synthetic VALIDATED fixture + synthetic content.publish grant + current C10 revision/fence → immutable _beta8_experimental_generations document + conditional _beta8_experimental_heads update + audit + C8 receipt`

The generated documents, head, promotion audit, authorization facts, C8 revision/history/receipt and mutation participant use the same C10 transaction. Retry returns the prior receipt; the participant is not applied a second time. A competing/stale revision or fence aborts the promotion. Earlier generation documents are append-only in this experiment.

## Explicit exclusions

No code writes `tracks`, `track_publications`, `activity_publications`, `nodes`, public generation heads, or Beta 5 staging records. No endpoint, reader, import writer, startup hook or publication process is connected. No real batch, source hash, draft status, rubric, grant, credential or source curriculum can be promoted by this contract. `SYNTHETIC_FIXTURE_APPROVED` is a technical test state; it is not an editorial or pedagogical approval.

## Evidence required before any operational design can be considered

Besides human editorial authority, a future operation needs verified source-manifest integrity, complete relation/contract validation, approved rubric state, resource grant, policy/session version, revision/fence, transaction topology, all competing writer containment, reader generation pinning, learner-history preservation, idempotency reconciliation, audit ACL/retention, recovery and rollback procedure. ADR-008 remains blocked, so none of these experimental tests authorize operational promotion.
