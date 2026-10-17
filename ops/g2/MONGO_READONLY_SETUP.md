# G2 MongoDB read-only account — staging only (NOT EXECUTED)

**This is a preparation for review, not an authorization to change MongoDB.** The source file `mongo-create-readonly-user.js` is inert until an operator separately approves and runs it. No passwords are checked into GitHub.

## Fixed target

- MongoDB container on VPS: `3jo4k9aes1iqn4qlqqeyyh4y` (verify actual ID before proceeding).
- Docker network: `trilhacode-staging-network`; no port exposure.
- Database: `trilhacode_staging` **only**.
- New account name: `trilhacode_g2_ro`.
- Account created **in** `trilhacode_staging` (thus application URI uses `authSource=trilhacode_staging`).
- Exactly one role: `{role: "read", db: "trilhacode_staging"}`.
- Password unique, random, **at least 32 characters**. Don't reuse `root` or `trilhacode_api`.

## Verification/approval checklist

1. Confirm staging MongoDB container ID, network, authentication configuration, and backup/restore. Never identify Mongo by a generic name that might resolve to Dev Forge.
2. Confirm `mongosh` and the `passwordPrompt()` helper in the exact MongoDB container, and review the provisioning JS. The script refuses to run unless selected DB is `admin` and the target user does not already exist.
3. Obtain separate explicit user approval to **create this one MongoDB user**. This changes MongoDB user metadata only; no application documents/indexes/migrations/seeds.
4. Authenticated operator should access `mongosh` using the staging MongoDB administrator with `--authenticationDatabase admin` and **select `admin` as current database**, then run reviewed file interactively in a TTY. Do not include the admin password in command arguments, logs, issue text or the repository. No MongoDB port should be published.
5. After creation, verify `getUser("trilhacode_g2_ro")` in `trilhacode_staging` shows only role `read`. Verify login and that a read operation works while an attempted harmless write is rejected; use a disposable staging-only test database/collection only if independently authorized. Avoid any write test on real collections.
6. Once separately authorized, build `/etc/trilhacode-g2/preflight.env` as root-only file (directory `0700`, file `0600`) with `ENV=staging`, `DB_NAME=trilhacode_staging`, and `MONGO_URL` for the staging MongoDB service. For this account, set `authSource=trilhacode_staging` and percent-encode reserved characters in user/password. Keep URI and secrets out of GitHub; never echo them.
7. **Do not run G2 preflight until** read-only credentials, image-pull access and SSH forced-command guard are independently validated and approved.

## Scope limitations

This change does **not** create any MongoDB user, alter roles for existing users, change application connection credentials, modify documents or indexes, publish any ports, deploy, or touch Coolify/Dev Forge. The JS file does not perform `updateUser` or `dropUser`; an existing name makes it stop instead of modifying it.

Important: `read` is authorization at the database scope, not automatic guarantee that the backend preflight is read-only. The existing `preflight-indexes` code should still be reviewed for command behavior; MongoDB `read` prevents writes regardless of application intent.
