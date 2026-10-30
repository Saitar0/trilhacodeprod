# Beta 8 — IAM inventory

## Runtime currently versioned

The active API resolves an access JWT in `backend/security.py::current_user`, requires an active `auth_sessions` record through `backend/services/sessions.py`, loads the user from `users`, rejects disabled accounts, checks `token_version`, and attaches permissions from the static `backend/constants.py::PERMISSIONS` matrix. `backend/permissions.py::require` checks only the role-to-permission mapping. These are verified properties of this checkout; they do not prove the deployed runtime or database roles.

The roles `admin`, `editor`, and `student` are mapped to global permission sets in Python. In particular, `admin` and `editor` include `content.write`; no resource grant is consulted by `permissions.require`. `can_view_track` permits staff by global read permission, or a public/published track without `_import_state`. That helper does not implement an editorial mutation grant.

No active IAM schema for track grants was found in the current request dependencies. The C11–C12 grant ledger (`experimental_editorial_grants.py`, `experimental_editorial_iam_authority.py`) is explicitly synthetic and disconnected from routes.

## C8–C16 contracts reused in the isolated proof

* C8/C10: one monotonic track revision, expected-revision CAS, fencing epoch, operation identity, idempotent receipt, history and transaction participant.
* C11/C12: synthetic principal, active session, operation-specific global permission, explicit track grant, grant epoch, signed server capability, and a conditional write to the authorization facts inside the C10 transaction.
* C13–C16: static 17-writer inventory, integration plan, and evidence that a MongoDB `readWrite` identity can bypass application CAS/fencing/audit by writing a protected collection directly.

Beta 8 composes these existing mechanisms for one synthetic draft-block update. It does not replace active JWT/session handling, change the global permission table, or make the experimental grant collection an operational IAM store.

## Ordering and revocation

The experimental transaction conditionally updates the current principal, session, and grant records before applying the content participant. Those writes share the C10 MongoDB transaction and compete with revocation updates. The persistent test separately exercises a grant revoked after preparation and before commit; that decision is rejected with no content change. C12 contains additional independent-client race tests; the Beta 8 harness adds its own two-writer CAS race.

This is a test-database linearization contract only. The static Python permission matrix has no persisted policy epoch, deployed session/grant storage is not proven to participate in the same transaction, and external IAM cannot be made linearizable by a second pre-write check. C15's hybrid policy-version plus coordinated-drain dependency remains open.

## Deny-by-default matrix (experimental slice)

| Action | Actor facts | Resource facts | Decision |
|---|---|---|---|
| Edit synthetic draft block | Active editor principal, active non-expired session, `content.write` | Track resolved from stored block; active grant for exact `block.update`; expected revision/fence current | Allow only through Beta 8 boundary and C10 transaction |
| Edit block with missing/revoked/out-of-scope grant | Any | Exact track does not match active grant | Deny; no C10 preparation or content write |
| Promote a synthetic generation | Active editor principal/session, `content.publish` | Synthetic validated batch, exact track grant, C10 revision/fence current | Allow only into `_beta8_experimental_*` collections |
| Promote real/revised curriculum | Any | Not a synthetic Beta 8 fixture | Deny by contract; no real source is accepted |
| Direct write using runtime/preparer Mongo identity | Any | Editorial or promotion collection | MongoDB rejects it in the tested role configuration |
| Publish or alter operational generation | Any | Operational publication collections | No Beta 8 service path; authority role has no such grant |

This table does not define all application actions or grant administrators global scope. Any unlisted action is outside this experiment and remains denied for the Beta 8 services.
