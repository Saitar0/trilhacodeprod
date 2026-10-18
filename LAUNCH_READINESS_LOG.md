# Trilha Code — Launch Readiness Work Log

Updated: 2026-10-18 (America/Sao_Paulo)
Audit base: `55d08dd734e862d46be91575226181b6bc9596b2` (`origin/main` at session start)

## Current mission

Mission 12 — continue release-readiness work from passing PR CI; the remaining signup and G2 gates need policy or operator action.

## Mission history

### Mission 1 — repository and merge checkpoint

- Confirmed `origin/main` at `55d08dd734e862d46be91575226181b6bc9596b2` and created a clean detached audit worktree at that SHA.
- Directly queried run [39099796575](https://github.com/Saitar0/trilhacodeprod/actions/runs/39099796575): exact SHA, overall success; `compose-config`, `backend`, `frontend`, and `e2e` jobs succeeded; staging and production deploy jobs were skipped.
- Original checkout is 15 commits behind remote main and contains uncommitted backend/frontend tests, deploy/docs changes, Phase 3 operational documents, and a local QA password-reset script. These files were left untouched. The QA script is not intended for release.
- Earlier checks on that original dirty checkout: backend isolated unit tests 33/33, frontend tests 9/9 when run with one worker, frontend typecheck/lint/build passed. These are not evidence for the audit SHA.
- G2 operational status remains pending: private GHCR image access, SSH key, network topology, and VPS component installation have not been verified in this environment.

### Mission 2 — deploy-trigger safety

- Confirmed the `main` workflow automatically retried Coolify deploy webhooks (`curl --retry 3`), which may enqueue duplicate deployments if a response is lost after acceptance.
- Removed retries from both deploy jobs and documented that ambiguous results must be checked in Coolify before retrying; an HTTP response does not prove deployment readiness.
- Added a unit-level workflow contract regression test to prevent automatic webhook retries from returning.

### Mission 3 — isolated release tests

- Backend unit tests on the exact `main` base: 82 passed, 35 skipped (Docker Engine contract checks skip when their environment is unavailable); Python compileall passed.
- Backend integration suite: 73 passed against a disposable Mongo 7 container, dedicated Docker network, tmpfs-only storage, 512 MiB/0.5 CPU limits, and loopback-only port. The fixture generated and dropped its unique `test_<uuid>` database.
- Frontend on the exact `main` base: 9 Vitest tests, typecheck, lint, production build and `npm audit --audit-level=high` passed; audit reported 0 vulnerabilities.
- Docker verification after both isolated test runs confirmed the disposable containers/networks/ports were removed and all 16 pre-existing container IDs remained unchanged.
- Browser E2E discovery found 5 tests. Execution was blocked because starting Vite through the command executor was rejected by its policy; the API was stopped and its isolated Mongo/network were removed. No workaround was attempted.

### Mission 4 — production origin and cookie configuration

- Reproduced that production settings accepted `https://app.example.com` with `COOKIE_DOMAIN=.example.com`, and accepted frontend URLs with paths. IANA identifies example domains as reserved for documentation and unavailable for registration; see [IANA reserved domains](https://www.iana.org/domains/reserved).
- Updated production validation to reject reserved/example hosts, non-origin HTTPS URLs and a cookie domain unrelated to `FRONTEND_URL`. Updated deployment guidance and added 12 deterministic settings tests; all passed.
- Re-ran backend integration after the validation change: 73 passed on a disposable Mongo. The final `.local` denylist extension only needs the settings/unit suite rerun.

### Mission 5 — read-only Coolify inventory and staging cookie defaults

- Read-only team-scoped Coolify inventory confirmed the Trilha Code project currently has one API application and one MongoDB resource. The staging API is `exited:unhealthy`, has no container present, no registry image configured, health checking disabled, and no deployment history. The staging Mongo is `running:healthy` and private.
- Staging Mongo has no Coolify backup schedule. No backup/restore job was run.
- Listed environment key names only (never values): API keys include `ENV`, `DB_NAME`, `FRONTEND_URL`, `CORS_ORIGINS`, `MONGO_URL`, and `JWT_SECRET`; there is no `COOKIE_SECURE` key. No database env keys were returned. Settings previously defaulted secure cookies only in production, so staging would emit cookies without `Secure` unless manually configured.
- Changed runtime default to secure cookies for both staging and production, and make explicit `COOKIE_SECURE=false` a staging configuration error. Added two tests; final unit suite is 84 passed / 35 skipped. Python compileall, YAML parse, and whitespace checks passed.
- This is code-only; it does not change the live Coolify resource. A new backend image and reviewed deployment would be required before the staging behavior changes.

### Mission 6 — access-control review and CI lint repair

- Reviewed API route guards and service checks for tracks, nodes, progress, notes, reviews, and submissions. Public student reads filter to published public tracks/nodes and student-owned data; administrative mutations require role permissions. No concrete authorization bypass was reproduced in this pass.
- PR #24 CI run `39101340050` on merge SHA `da341f6a77af8a41c1ee25846b478d53d96bd038`: Compose, frontend (typecheck/lint/unit/build/dependency audit), E2E and 119 backend unit tests passed; Ruff failed on three import-order violations in changed files; downstream backend checks were skipped, and deploy jobs were skipped.
- Corrected only the three Ruff import-order findings. Local `ruff check backend` passed; local backend unit suite passed 84, with 35 Linux runner-only Docker contract tests skipped. No Mongo integration or deploy was run for this formatting-only correction.
- Browser E2E on CI passed all student and administrator scenarios against the disposable Mongo service, including student progress and submission, and administrator track editing/import/version comparison.

### Mission 7 — public lesson content review

- Reviewed the deployment/backup runbooks and G2 isolation docs without triggering infrastructure operations. The G2 guardrails preserve Mongo's existing Coolify network and forbid attaching Dev Forge; the docs keep host activation, backup/restore proof, and G2 dispatch as separate gates.
- Found malformed closing punctuation in the Fase 4 container-networking solution, duplicated in its import JSON. Corrected the Markdown source and import copy so the example now uses `--network estudo-net` and hostname `estudo-db` correctly.
- Validated the import JSON parses and the corrected solution appears identically in both copies. No course data was imported into any live database.

### Mission 8 — video provider and production CSP alignment

- Confirmed `VideoBlock` constructs Vimeo iframe URLs at `player.vimeo.com`, while all three production Nginx CSP declarations allowed only YouTube frames. This would block supported Vimeo embeds in deployed production.
- Added `https://player.vimeo.com` to each CSP declaration and corrected the deploy guide to list both supported providers.
- Frontend unit suite passed 9/9 after the edit; `git diff --check` passed. Production image/reverse-proxy integration remains pending CI; no deploy was performed.

### Mission 9 — public registration abuse controls

- Confirmed `/cadastro` is an unauthenticated public route; backend registration accepts a six-character password and has no registration rate limit or email verification. Login has a separate failure limit, which does not constrain account creation.
- Recorded this as a launch policy gate instead of inventing a signup quota or depending on an unconfigured email service. Before publicly opening registration, select and implement anti-abuse controls, password policy, and the corresponding user experience.
- Ran a targeted secret-pattern scan over tracked files for common cloud access keys, GitHub tokens, private-key headers, credentialed MongoDB URIs, and long literal password/secret/token assignments: no tracked matches. This is a targeted check, not a comprehensive secret audit.

### Mission 10 — production frontend image validation in CI

- Found that frontend CI built the Vite app but did not build `frontend/Dockerfile.prod` or parse its Nginx configuration, leaving the production CSP and static-server config outside the CI gate.
- Added CI steps to build the frontend production image with a non-routable placeholder backend origin and run `nginx -t` in that ephemeral image. The job does not push the image.
- Local workflow YAML parsing and `git diff --check` passed. The runner-level Docker build and Nginx parse await CI; no image was built on the shared local Docker host.

### Mission 11 — production image checks and latest PR CI

- PR #24 CI run `39101916285` passed all validation jobs on head `b93a10b1283ee14f1c5f9e6ab19fa9d20c851c8d`: Compose, backend unit/Ruff/integration/config/image/dependency audit, frontend typecheck/lint/unit/build, production frontend image build, `nginx -t`, frontend dependency audit, and isolated student/admin E2E.
- Staging and production deploy jobs were skipped as expected for a pull request. No image was pushed to a registry.
- Prior run `39101875571` also passed Compose/backend/frontend/E2E on SHA `3a0091f81362a1bac7a9b49d59b0c24a2018a926`; run `39101760653` passed on the Vimeo-CSP SHA `fd99bff6e157363df55ef1597de242c3bfbd13cb`.
- PR #24 remains open and unmerged. Its branch has no deployment evidence; production/staging operational gates remain pending.

## Evidence and test ledger

| Date | Scope | Result | Limits |
| --- | --- | --- | --- |
| 2026-10-18 | `origin/main` SHA | `55d08dd734e862d46be91575226181b6bc9596b2` | Fetch/refs verified locally |
| 2026-10-18 | PR #23 post-merge CI, run 39099796575 | Success; compose/backend/frontend/e2e pass; deploys skipped | Directly retrieved via connected GitHub Actions connector |
| 2026-10-18 | Original dirty checkout unit/frontend checks | Passed as recorded above | Different base; not release evidence |
| 2026-10-18 | Main backend unit suite / PR branch revision | 84 passed, 35 skipped | Includes workflow, origin, and staging-cookie contracts |
| 2026-10-18 | Main backend integration | 73 passed | Disposable isolated Mongo 7, no persistent mounts; cleaned and verified |
| 2026-10-18 | Main frontend checks | 9 Vitest; typecheck/lint/build/audit passed | `npm audit` found 0 vulnerabilities |
| 2026-10-18 | Playwright browser E2E | 5 tests discovered; not executed | Executor blocked Vite server start; no workaround |
| 2026-10-18 | PR #24 CI run 39101340050 | Compose, frontend and E2E passed; 119 backend unit tests passed; Ruff failed | Exact failure was three import-order violations; remaining backend steps were skipped |
| 2026-10-18 | Ruff repair in PR #24 worktree | `ruff check backend` passed; backend unit suite 84 passed / 35 skipped | Changes only reorder imports; awaiting CI on corrected commit |
| 2026-10-18 | Container networking lesson source/import copy | Malformed inline-code closing delimiters corrected in both files; JSON parse passed | No live import or database write |
| 2026-10-18 | Video CSP and embed-provider contract | Vimeo player origin added to all 3 production CSP declarations; frontend tests 9/9 passed | CI/image validation pending; no deployment |
| 2026-10-18 | PR #24 CI run 39101630737 | Compose and frontend passed; backend and E2E still running at checkpoint | Head `05150db965c67b98359191da55c0e71a4465d11d`; superseded by later content commits |
| 2026-10-18 | Public signup/auth policy review | Open signup confirmed; 6-character minimum, no signup throttle/email verification; targeted tracked-secret scan had no matches | Anti-abuse policy and email service are not configured in this environment |
| 2026-10-18 | Production frontend CI gate | Added ephemeral production image build and `nginx -t`; workflow YAML parsed locally | Await CI on the new commit; no registry push |
| 2026-10-18 | PR #24 CI run 39101916285 | All validation jobs passed, including production frontend image build, `nginx -t`, disposable Mongo integration and Playwright E2E; deploys skipped | Exact PR head `b93a10b1283ee14f1c5f9e6ab19fa9d20c851c8d`; not a staging/production deployment |

## Findings

- `main`'s deploy steps treated webhook HTTP acceptance as job success and did not wait for deployment completion/readiness; docs now state the operator checks required.
- Coolify deployment remains non-sequential and not readiness-gated. Automatic retries are removed, but production deploy safety is not fully implemented.
- Production hostname/cookie validation is stricter, but DNS, exact production origins and Coolify environment values remain unverified operationally.
- Public registration currently has no email verification or creation-rate limit and accepts six-character passwords; decide and implement signup abuse controls before public exposure.

## Blockers

- No SSH/Hostinger console access is established. Coolify access in this session is limited to team-scoped read-only metadata; do not infer G2 completion.
- Current read-only Coolify evidence: the Trilha Code staging API has no container, no registry image, disabled health checks, and zero deployments; the staging Mongo has no backup schedule.
- The local browser E2E could not start because the executor blocked the Vite server command; CI run 39101340050 passed the E2E job on PR #24, while backend CI failed only at Ruff and has been corrected locally.
- Actual environment values, SSH secrets/fingerprint, GHCR pull identity, and network memberships remain unverified; do not read or alter secrets to resolve this.
- Public signup abuse controls and password requirements need a product decision and code/UI implementation before enabling broad registration.

## Next actions

1. Continue public-signup mitigation work once the product policy is established; no email delivery service is configured here.
2. Keep G2 blocked until image, SSH identity, read-only Mongo account, dedicated network, backup/restore, and host runner requirements are met and separately approved.
3. Public launch requires real staging evidence, backup/restore proof, a healthy API, and a readiness-gated deployment process.

### Missão 12 — integração e gates operacionais após PR #25 (18/10/2026)

- PR #25 integrada em `f461ca03e0847541911b926efc87b35c99874124`. Consulta direta aos jobs da CI pós-merge #39109006957 confirmou backend, frontend, E2E e Compose com `success`; deploy de staging e produção foram `skipped`. O estado informado pelo supervisor foi confirmado independentemente para esta execução.
- Nova consulta somente leitura do Coolify confirmou recurso Mongo `trilhacode-staging-mongodb`, UUID `3jo4k9aes1iqn4qlqqeyyh4y`, MongoDB standalone 7, banco inicial `trilhacode_staging`, privado/saudável e sem porta publicada. Volumes: `/data/configdb` com storage UUID `mbic79qapkm95aiwdythvzjg` e volume `3jo4k9aes1iqn4qlqqeyyh4y-mongodb-configdb-n3ry5kmbvok7btuv9nebymsr`; `/data/db` com storage UUID `hi6bplsj8ibyjofxflaa1vgc` e volume `3jo4k9aes1iqn4qlqqeyyh4y-mongodb-db-n3ry5kmbvok7btuv9nebymsr`. Volumes persistem os dados, mas não são backup.
- Consulta de agendas retornou `backups: []`; não há agenda, execução ou restauração comprovada. Nenhum backup foi criado. O canal Coolify disponível não oferece ferramenta de mutação de backup.
- O UUID Coolify foi confundido com ID Docker real no runner G2. O runner agora valida formato de ID Docker de 64 hexadecimais e inspeciona somente o ID fixado no arquivo de ambiente root-only. Teste de regressão rejeita o UUID de recurso Coolify antes de iniciar qualquer container. A documentação também registra que ID/nome/redes/aliases reais não estão expostos pela metadata disponível e não devem ser presumidos.
- Evidência operacional: a API de staging continua sem container implantado/histórico; o Coolify não dá logs de processo para recurso parado. Dockerfile local define `/health`, mas configuração do recurso mostra healthcheck desativado e caminho `/`; a divergência é comprovada, a causa original do container ausente não é. Não foi feito deploy, reinício, alteração de banco/rede/segredo, criação de backup, G2 ou operação no Dev Forge.
- Inspeção atual da aplicação confirmou domínios `api.staging.saitaro.tech` e `www.api.staging.saitaro.tech`, Dockerfile `/backend/Dockerfile.prod`, porta 8000, sem imagem/tag de registry, healthcheck Coolify desativado e caminho `/`. Coolify está configurado para branch `main`, divergindo do procedimento e do job versionado que limitam staging à branch `staging`; resolver essa identidade antes do deploy. Compose path `/docker-compose.yaml` também diverge de `compose.yaml`, mas sua relevância é incerta no build pack Dockerfile.
- SMTP: avaliação oficial em 18/10/2026 adicionada ao runbook. Resend é a opção inicial recomendada para menor atrito de staging (plano grátis limita a 100/dia); Postmark é alternativa focada em transacional; SES Essentials custa menos por volume, com maior esforço AWS e sandbox de 200/dia/1 por segundo. Nenhuma conta, domínio verificado, remetente ou credencial está disponível; entrega real não foi testada.
- Restauração isolada não foi executada. A sessão Windows não tem `pytest`/`ruff` no Python padrão ou runtime bundled; o harness do runner requer Bash POSIX, `jq` e `flock`, indisponíveis neste host (WSL sem Bash). Validação de sintaxe do runner passou com Git Bash. CI Linux deverá executar o harness completo após PR; não usar Docker compartilhado com imagens do Dev Forge.
- Bloqueios G2: imagem GHCR privada/digest atual ainda não verificados e pin atual não contém o módulo do preflight; fingerprint/known_hosts e ID/redes/aliases Docker não disponíveis; usuário Mongo read-only não provisionado/verificado; backup/restore não comprovados; runner/manifesto não instalado. G2 não foi disparado.
- PR operacional #26 aberta em `https://github.com/Saitar0/trilhacodeprod/pull/26`, branch `codex/g2-container-identity-fix-20261018`, head `34dce906dcf3ad4ba9d805e084877827aae4ea5f`. Run CI #39109642160 concluiu com sucesso em backend (testes sem Mongo, Ruff, integração com Mongo descartável, compileall, validação de config, build de imagem e auditoria de dependências), frontend (typecheck, lint, unit, build, imagem de produção, `nginx -t`, auditoria), Compose e E2E aluno/admin. Deploys foram pulados. Run é pré-merge e não homologa staging/produção.
- Próxima ação: manter PR #26 sem merge automático e encaminhar para revisão; depois obter por canal autorizado leitura da VPS para inspecionar Docker e preparar backup consistente/restaurável. Manter recuperação da API bloqueada até restore, imagem por digest, branch/origem, configuração/rollback e impacto compartilhado serem verificados.
