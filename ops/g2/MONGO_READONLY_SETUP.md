# G2 MongoDB read-only account — staging only (existing role observed; provisioning not authorized)

**This is a preparation for review, not an authorization to change MongoDB.** The source file `mongo-create-readonly-user.js` was not used in the read-only VPS inspection. The host already reports the user `trilhacode_g2_ro` with role `read` on `trilhacode_staging`; its effective actions have not been independently enumerated. Do not run the creation script or change roles unless a later inspection proves that is necessary and separately authorized. No passwords are checked into GitHub.

## Target identity (partially verified)

- Coolify standalone MongoDB resource UUID: `3jo4k9aes1iqn4qlqqeyyh4y` (`trilhacode-staging-mongodb`, project Trilha Code). This is **not** a Docker container ID.
- Coolify reports MongoDB 7, healthy, private and without a published port. Its persistent mounts are `/data/configdb` and `/data/db`; Coolify storage UUIDs are recorded in the launch log. No backup schedules are configured.
- The full Docker container ID, name, operational network attachments, and aliases were verified by read-only inspection on the authorized VPS on 2026-10-19. Keep the full container ID out of this repository; do not substitute the Coolify resource UUID or assume a Docker network name if the container is recreated.
- Database: `trilhacode_staging` **only**.
- New account name: `trilhacode_g2_ro`.
- Account created **in** `trilhacode_staging` (thus application URI uses `authSource=trilhacode_staging`).
- Exactly one role: `{role: "read", db: "trilhacode_staging"}`.
- Password unique, random, **at least 32 characters**. Don't reuse `root` or `trilhacode_api`.

## Verification/approval checklist

1. Confirm the full staging MongoDB Docker container ID, network, authentication configuration, and backup/restore. Never identify Mongo by a generic name that might resolve to Dev Forge. Preserve every existing operational network attachment.
2. Confirm the user's effective actions and database scope with an authorized read-only inspection. If any identity change is proposed, first establish that the existing user is absent or invalid and review the exact change. The provisioning script refuses to run unless selected DB is `admin` and the target user does not already exist.
3. Do not run the provisioning script while the existing `read` role remains present and needs no change. Any later MongoDB user/role mutation requires separate review and explicit authorization.
4. Authenticated operator should access `mongosh` using the staging MongoDB administrator with `--authenticationDatabase admin` and **select `admin` as current database**, then run reviewed file interactively in a TTY. Do not include the admin password in command arguments, logs, issue text or the repository. No MongoDB port should be published.
5. After creation, verify `getUser("trilhacode_g2_ro")` in `trilhacode_staging` shows only role `read`. Verify login and that a read operation works while an attempted harmless write is rejected; use a disposable staging-only test database/collection only if independently authorized. Avoid any write test on real collections.
6. Once separately authorized, build `/etc/trilhacode-g2/preflight.env` as root-only file (directory `0700`, file `0600`) with `ENV=staging`, `DB_NAME=trilhacode_staging`, and `MONGO_URL` for the staging MongoDB service. For this account, set `authSource=trilhacode_staging` and percent-encode reserved characters in user/password. Keep URI and secrets out of GitHub; never echo them.
7. **Do not run G2 preflight until** read-only credentials, image-pull access and SSH forced-command guard are independently validated and approved.

## Scope limitations

This change does **not** create any MongoDB user, alter roles for existing users, change application connection credentials, modify documents or indexes, publish any ports, deploy, or touch Coolify/Dev Forge. The JS file does not perform `updateUser` or `dropUser`; an existing name makes it stop instead of modifying it.

Important: `read` is authorization at the database scope, not automatic guarantee that the backend preflight is read-only. The existing `preflight-indexes` code should still be reviewed for command behavior; MongoDB `read` prevents writes regardless of application intent.
