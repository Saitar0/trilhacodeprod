# G2 — VPS executor (review-only; NOT INSTALLED)

The existing GHCR image below is a legacy pin and is **not compatible** with the new runner protocol in this branch. It does not contain `backend.g2_preflight` and must not be used to activate this implementation:

```text
ghcr.io/saitar0/trilhacodeprod-backend@sha256:a6bf47a3fb1c8019678c85ce5d6d6b055a61e547c62681865f8fd1be20fad71e
```

This branch changes software and test sources only. It does not install anything on the VPS, configure GHCR access, create a MongoDB user, start a container, deploy via Coolify, publish an image, or run the preflight. **Review before merging or executing.**

## Security model

- SSH account `trilhacode-g2` is already present, password disabled, and outside `sudo`/`docker` groups.
- The installer takes **only a dedicated Ed25519 public-key file path** and refuses to overwrite any nonempty authorized_keys or existing G2 scripts/policy.
- The key entry enforces `restrict,command="/usr/local/sbin/trilhacode-g2-preflight-guard"`.
- The guard checks `SSH_ORIGINAL_COMMAND` exactly equals `trilhacode-g2-preflight` and can call **only** the root-owned preflight runner via passwordless sudo. The runner is root-owned mode 0700; `sudoers` allows exactly that path with no user-provided flags.
- Runner accepts no arguments, pins an immutable backend image, checks the expected staging container ID and a dedicated internal Docker network, validates the independent manifest, and requires `preflight.env` to be root-owned mode 0600. MongoDB keeps its existing operational network attachments and joins G2 as a secondary network; the dedicated G2 network contains only the expected MongoDB before the run. The ephemeral container's configured network mode is verified before its process starts, and its actual endpoint set must contain only G2. A root lock prevents overlapping invocations.
- The pinned image's Dockerfile has no non-root `USER`, so the runner explicitly sets UID/GID `65532:65532`. It runs the backend in an ephemeral restricted Docker container with no ports, host mounts, privileges or Docker socket; read-only filesystem, resource limits and 180-second timeout.
- Backend output is captured to a root-only temporary file; GitHub gets **only counts** of `OK`, `AUSENTE`, `CONFLITO`, `DUPLICATAS`. No raw error strings or sample MongoDB keys are sent to GitHub.
- A nonzero command exit, conflict, duplicate, timeout or failed prerequisite returns a failure. Missing indexes are expected before G4.

## Dependencies BEFORE real execution — require separate authorization

1. Independently review the scripts and host state. `3jo4k9aes1iqn4qlqqeyyh4y` is the Coolify database resource UUID, not a Docker container ID. The runner now takes the expected full 64-character Docker container ID only from the protected `G2_MONGO_EXPECTED_CONTAINER_ID` setting and inspects that exact ID; if the resource is recreated, stop and review rather than weakening the comparison.
2. Install and configure a dedicated MongoDB account with **`read` only on `trilhacode_staging`** (not `readWrite`; do not reuse API password). Verify access is restricted to the staging DB. This procedure is NOT implemented in this PR.
3. As root, create `/etc/trilhacode-g2/preflight.env` (directory 0700, env file owner root mode 0600) with exactly the six variables documented in `docs/g2-staging-preflight-automation.md`; include `ENV=staging`, `DB_NAME=trilhacode_staging`, expected Mongo host/port/full container ID, and a properly URL-encoded staging `MONGO_URL` with explicit `directConnection=true`. **Do not paste credentials to chat, commits or logs.**
4. After this code is reviewed and integrated, separately build and publish a backend image from the exact approved source revision. Review provenance and immutable digest, then update the runner pin only through a separately authorized host change. Provision a **read-only** GHCR credential on the VPS and pull that reviewed digest in a separate approved operation. The installer and runner **never log into GHCR or pull images**.
5. Review the existing SSH `Match User trilhacode-g2` configuration; validate with `sshd -t`. Do not weaken other users' SSH access. Avoid placing the root SSH private key in GitHub.
6. Provision the dedicated public key securely on the VPS outside the repository; review and explicitly authorize running `ops/g2/install-g2-host.sh /root/your-dedicated-g2-public-key.pub` as root from a **verified repository checkout**. This creates two root-owned scripts, a narrowly scoped sudoers file, and one forced-command key entry. It performs **no preflight**.
7. Independently confirm the VPS SSH host-key fingerprint and configure GitHub Environment `staging-preflight` secrets `G2_STAGING_SSH_HOST`, `G2_STAGING_SSH_USER=trilhacode-g2`, `G2_STAGING_SSH_KEY`, `G2_STAGING_SSH_KNOWN_HOSTS`. Secrets must never be printed. Restrict SSH network access as feasible. 
8. Verify resistance to alternate SSH commands, TTY, agent/port forwarding, scp and command injection; verify no sudo Docker access except the fixed runner. Only after explicit approval, trigger the existing manual GitHub Actions staging preflight workflow.
9. Complete G1 backup/offsite verification and preserve independent explicit approval for G3/G4/G5/G6. The G2 read-only preflight does not authorize those gates.

## Operational caveats

- The installer is **single-use** by design; running it twice stops rather than silently rewriting access controls.
- The runner uses a root-only process lock, random invocation name and label, and verifies the container ID/label before cleanup. If ownership or cleanup cannot be established, it fails closed and may leave an orphan for manual host inspection; do not report a pass.
- GHCR image digest pins content, but independent provenance validation of the GitHub workflow and approved commit is still required before production-sensitive use.
- Docker `Internal=true` limits ordinary routing through the G2 bridge but is not proof of absolute host isolation. Host-gateway services, custom routes/firewall rules, other bridges, published ports, and privileged Docker administrators remain in the host trust boundary and require separate review.
- `preflight.env` is presented to Docker as container environment and is readable by host root/Docker admins; it is not exposed to the GitHub SSH account. Docker administrators are already privileged.
- Mongo errors and raw findings are intentionally not exposed to GitHub. Operational diagnosis must occur securely on the VPS.
- This source has not yet been executed against the VPS; review shell, sudo policy and Docker security options on the target OS before installation.
