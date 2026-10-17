# G2 staging preflight — gated GitHub Actions bridge (NOT YET ACTIVE)

This is a **proposal**, not permission to provision an SSH account or execute a database preflight.

## What the workflow does

The workflow `.github/workflows/g2-staging-preflight.yml` is triggered exclusively by `workflow_dispatch`. After an optional GitHub Environment approval, it sends the fixed command `trilhacode-g2-preflight` over SSH, using a dedicated key. It does **not** check out code, install a GitHub runner on the VPS, copy secrets to the VPS, or invoke Coolify deploy.

**Do not run** before the host-side restricted command and all controls below are independently reviewed, installed, and tested.

## Required GitHub configuration (not created by this change)

Create environment `staging-preflight` with required reviewers (if the repository plan supports them), restricted to the intended branch, and four *environment secrets*:

- `G2_STAGING_SSH_HOST`: VPS public hostname/IP (never a database endpoint).
- `G2_STAGING_SSH_USER`: dedicated non-root preflight SSH account.
- `G2_STAGING_SSH_KEY`: dedicated private SSH key for this single operation.
- `G2_STAGING_SSH_KNOWN_HOSTS`: independently verified SSH server host-key entry (do **not** blindly trust `ssh-keyscan` output).

Never use the existing root key or a Coolify/MongoDB token. No secret values belong in the repository, screenshots, issue text, or logs.

## VPS-side design requirement — separate authorization needed

A dedicated SSH account must be limited in `authorized_keys` with a **forced command** and restrictive forwarding/TTY options, for example:

`restrict,command="/usr/local/sbin/trilhacode-g2-preflight-guard" ssh-ed25519 PUBLIC_KEY`

This is illustrative, NOT a provisioning command. The server-side guard must ignore/reject arbitrary `SSH_ORIGINAL_COMMAND` values other than the exact fixed request. It must not permit interactive shell, port forwarding, scp, arbitrary commands, or unrelated Docker administration.

**Docker socket access is root-equivalent.** Do not put the GitHub-facing SSH user in the `docker` group or give unrestricted `sudo docker` access. A separately reviewed root-owned wrapper with narrowly defined execution rights may run the preflight using the approved image and a fixed Docker network; it must verify all inputs and avoid evaluating or interpolating attacker-provided shell strings.

Host-side execution guard requirements:

1. Confirm approved backend revision is exactly `65857f5a4d26b026f7b064862bebc29091713d9a` and use an image verified/built from this source on the VPS (GitHub runner's previous image was **not** transferred).
2. Target only `trilhacode-staging-network` and the intended MongoDB container `3jo4k9aes1iqn4qlqqeyyh4y`; verify the name and network before running.
3. Use a **separate MongoDB read-only credential** for `trilhacode_staging`, stored **only on the VPS** with restrictive permissions; never reveal or print the URI or environment file. Existing `trilhacode_api` role `readWrite` is broader than necessary.
4. Execute exclusively `python -m backend.manage preflight-indexes` in a nonprivileged, ephemeral container with `--network trilhacode-staging-network`, no published ports, no mounts except an explicitly justified secure environment injection mechanism, no Docker socket, no added capabilities, read-only filesystem if compatible, resource/time limits, and default entrypoint overridden.
5. Ensure output is sanitized before being sent to Actions. The current `DUPLICATAS` messages can contain sample document identifiers and key values: **do not publish raw output**. Return status counts and safe index identifiers, not document samples.
6. Preserve the program's exit code: fail on authentication/network errors, CONFLITO, DUPLICATAS, timeout, and other exceptions. AUSENTE is expected before G4.
7. Keep G1 release gates (off-VPS backup hash/retention) and G3/G4/G5 approvals independent.

## Non-goals

No SSH account, keys, MongoDB user, environment files, image or scripts are created by this PR. It does not perform any build, preflight or deploy. No changes to Dev Forge or to Docker networks/firewalls/Coolify are authorized.

Before activation, perform a host-only review of the wrapper, least-privilege permissions, image provenance, output filtering, and failure cases. Confirm with the user before any infrastructure writes.

## Verificação de identidade SSH antes da ativação

O workflow atual não define `-p` nem uma opção `Port`; a conexão usa a porta SSH padrão 22. O valor de `G2_STAGING_SSH_HOST` é um secret e deve ser confirmado pelo responsável no GitHub Environment `staging-preflight`. Não infira o alvo a partir do IP público da VPS.

Antes de propor qualquer correção:

1. Em um console administrativo autenticado da VPS, consulte a linha da chave pública ED25519 com `sudo cat /etc/ssh/ssh_host_ed25519_key.pub` e calcule sua fingerprint com `sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub -E sha256`. Registre a linha pública e a fingerprint somente por canal privado; confirme que o console pertence à VPS esperada. A chave `.pub` é pública, mas não a copie para este repositório, tarefa, terminal compartilhado ou logs.
2. O responsável confere privadamente que o hostname/IP de `G2_STAGING_SSH_HOST` identifica essa VPS. A entrada de `G2_STAGING_SSH_KNOWN_HOSTS` precisa usar exatamente essa identidade; na porta padrão 22, a forma habitual é `host ssh-ed25519 BASE64_PUBLIC_KEY`.
3. Calcule a fingerprint da chave ED25519 na entrada conhecida, usando um arquivo temporário seguro sob controle do responsável, e compare os valores SHA256. Não copie secrets para este repositório, tarefa, terminal compartilhado ou logs.
4. Se identidade e fingerprint coincidirem, preserve os valores. Se a identidade host estiver errada, corrija somente `G2_STAGING_SSH_HOST`; se a chave estiver ausente ou for a chave pública errada para a identidade confirmada, atualize somente `G2_STAGING_SSH_KNOWN_HOSTS` com a entrada verificada. Se a fingerprint não coincidir, pare e investigue a identidade/rotação com o administrador.
5. Se o console autenticado estiver indisponível, pare aqui e registre o bloqueio. Não confie em `ssh-keyscan` sem comparação independente. Não desative `StrictHostKeyChecking`.

A correção do secret exige aprovação do responsável da infraestrutura. Disparar o workflow G2 exige aprovação separada, pois ele consulta o Mongo de staging e pode consumir recursos.

