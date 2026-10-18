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

- Hostinger access was subsequently established through the authenticated VPS web console for read-only inspection only (Mission 14). Local SSH authentication is still unavailable; the approved host key matches the local known-hosts pin, but the local identity was not authorized.
- Current read-only Coolify evidence: the Trilha Code staging API has no container, no registry image, disabled health checks, and zero deployments; the staging Mongo has no Coolify backup schedule.
- The local browser E2E could not start because the executor blocked the Vite server command; CI run 39101340050 passed the E2E job on PR #24, while backend CI failed only at Ruff and has been corrected locally.
- Actual environment values, GHCR pull identity, Mongo read-only user/role, and the identity/writer role of the second container on the Mongo network remain unverified; do not read or alter secrets to resolve this.
- The public-signup policy and application controls are merged through PR #25; staging email delivery, rate-limit behavior behind the production proxy, and end-to-end verification still require real environment validation.

## Next actions

1. Identify the active non-Trilha container connected to the staging Mongo network and establish whether it can write, using an authorized non-secret read path; do not detach or modify it.
2. Establish a database-scoped, consistent backup and disposable Mongo 7 restore proof with protected off-host retention. Hostinger snapshots are whole-VPS recovery points and must not be restored because they include shared services.
3. Keep G2 blocked until private image digest/provenance, runner version, SSH identity, read-only Mongo role, network isolation, and backup/restore requirements are verified.
4. Public launch requires real staging evidence, backup/restore proof, a healthy API, and a readiness-gated deployment process.

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

### Missão 13 — revisão PR #26 e descoberta de acessos operacionais (18/10/2026)

- Revisão independente do diff completo da PR #26 (`d88ad85b9c382f344833ce05637244e301f6be2c`): runner valida ID Docker completo de 64 hexadecimais lido do arquivo de ambiente root-owned `0600`, inspeciona exatamente esse ID e compara `.Id` antes de prosseguir. O teste regressivo injeta o UUID Coolify e confirma falha `TARGET_IDENTITY` antes de iniciar o container. Verificações de rede e identidade continuam fail-closed; não foi encontrado defeito impeditivo na PR.
- CI Linux pré-merge #39109934722 no head da PR: backend, frontend, Compose e E2E aluno/admin passaram. Deploys de staging e produção foram `skipped`; isto não homologa os ambientes.
- PR #26 integrada via squash em `41dc470c567bae50b7ebcf0662d45d43863980c9`. A CI pós-merge #39112747654 foi consultada diretamente: conclusão `success` nos jobs backend, frontend, Compose e E2E; deploy de staging e produção `skipped`.
- Inventário SSH local sem imprimir credenciais: Windows OpenSSH disponível; agente SSH parado/sem identidades; existe uma identidade Ed25519 local, e a configuração só associa `saitaro` ao host privado `192.168.1.200`. O DNS atual de staging coincide com endereço para o qual há chaves de host previamente armazenadas. Uma única tentativa não-interativa com `BatchMode`, `IdentitiesOnly` e `StrictHostKeyChecking=yes`, limitada a comandos de identificação e leitura Docker, foi recusada por `Permission denied`; nenhuma nova tentativa será feita com essa identidade. Não há outro arquivo de chave em `.ssh` nem sessão autenticada de navegador/app visível nesta sessão.
- O Coolify MCP confirma somente metadata de leitura: servidor gerenciado `localhost` (UUID `zw2xihhez3as8wvwx4epo6tz`, endereço interno `host.docker.internal`), usuário configurado `root`, porta 22, reachable. Nenhum terminal SSH/Coolify ou sessão Hostinger autenticada está exposto pelas ferramentas disponíveis. A tentativa de identidade local não foi autorizada pelo host; acesso operacional à VPS segue indisponível.
- GHCR: Docker usa credential helper local, mas a consulta sanitizada não encontrou entrada `ghcr.io`; `docker manifest inspect` do digest legado privado falhou por ausência de autorização (`unauthorized`). Não foi feito login nem tentativa de elevar privilégios. A imagem legada não foi validada nem contém evidência de compatibilidade com o runner atualizado.
- Mongo de staging permanece `running:healthy`, standalone MongoDB 7; consulta de agendas continua `backups: []`. Não existe execução nem restore comprovado. A API permanece `exited`, histórico de deploy vazio e sem container operacional. `/health` e `/ready` retornaram sem resposta HTTP validável: a tentativa local foi interrompida pelo Schannel por erro de cadeia TLS não confiável; nenhuma verificação TLS foi desativada. Isso não determina se o certificado remoto está incorreto ou se a raiz confiável falta somente neste executor.
- Nenhum backup, restore, deploy, G2, alteração de banco/rede/segredo, operação de terminal ou mudança em Dev Forge foi realizado. A CI não publicou imagem; deployment continua bloqueado por backup restaurável, escritores/janela consistentes, imagem privada compatível e digest/proveniência, SSH/host key autorizados, rede/IDs, usuário Mongo read-only, origem/configuração/rollback, e SMTP real.
- GitHub informou branch `main` sem proteção/configuração de status obrigatório na consulta; não foi alterada configuração de repositório. Para prontidão pública, habilitar proteção e gates de revisão/CI exige permissão administrativa autorizada e decisão operacional.
- Próxima ação: obter acesso humano autorizado à VPS (usuário/chave SSH permitidos e fingerprint de host confirmado) ou um terminal Coolify com escopo de leitura; então inventariar escritores, identidade de containers/redes e armazenamento antes de planejar backup. É necessária também autorização/configuração de um destino de backup externo com retenção e disponibilidade verificáveis. Até isso ocorrer, preservar os serviços e não executar G2, backup/restore ou recuperação da API.

### Missão 14 — inventário Hostinger, backup VPS e topologia Mongo (18/10/2026)

- O usuário disponibilizou sessões autenticadas da Hostinger e do Coolify. Acesso utilizado somente para leitura: console web da VPS confirma host `srv2032201`, usuário `root`, Docker `29.8.2`, e SSH ativo. Nenhuma configuração, chave, serviço ou dado foi alterado.
- A chave pública Ed25519 do servidor, consultada pelo fingerprint (sem imprimir conteúdo de chave), corresponde ao pin da mesma VPS no `known_hosts` local. A identidade SSH local continua sem autorização: a chave configurada localmente não corresponde à chave pública `coolify` exibida na Hostinger e a tentativa anterior foi negada; nenhuma chave foi adicionada nem nova tentativa de autenticação foi feita.
- Docker mostra somente o Mongo Trilha Code como container do projeto; MongoDB `mongo:7` está saudável, sem porta publicada, em `trilhacode-staging-network`. A imagem local resolve a `mongo@sha256:9650758f83af117fc96699f030a44f9300bed839734e67012f56df05b2fd6290`. Os aliases atuais observados são o UUID Coolify e o identificador Docker curto; não há alias `mongo`. A rede contém dois membros. O segundo está ativo e usa uma imagem da família Traefik; os metadados sanitizados não o identificam como recurso Trilha Code ou Dev Forge, mas sua identidade/owner não foi comprovada. A rede é `bridge`, `Internal=false`, `Attachable=true`; apesar de Mongo sem porta publicada, esse estado não satisfaz isolamento estrito. O peer não foi alterado. Ainda não está comprovado que ele não possa escrever no Mongo, portanto não há janela de consistência comprovada.
- O painel Hostinger mostra backup automático semanal e dois pontos de recuperação de VPS inteira (17 e 10/10/2026), armazenados fora do servidor segundo o painel, com substituição automática dos backups antigos e tempo estimado de restauração de 30 minutos. O restore substituiria a VPS completa, incluindo serviços compartilhados como Dev Forge; portanto não é um backup isolado do Mongo nem uma recuperação segura para teste. Nenhum backup, snapshot ou restauração foi iniciado.
- Não foi executado `mongodump`, pois a identidade de todos os escritores e uma janela consistente não estão comprovadas; também não há destino Mongo externo de retenção nem restauração descartável demonstrada. Mongo segue saudável e intocado.
- A tentativa de consultar roles do Mongo via `mongosh`, usando as variáveis do container sem revelar seus valores, retornou indisponível pelo console web. A causa específica não foi exposta nem repetida. Os nomes de variáveis de inicialização indicam credenciais raiz configuradas, mas não provam a existência nem os privilégios do usuário G2 somente leitura. Nenhuma conta foi criada ou alterada.
- A lista de recursos team-scoped do Coolify continua mostrando a API de staging como `exited:unhealthy` e o Dev Forge como `running:unknown`. A configuração do Dev Forge não foi aberta; nenhum recurso dele foi alterado.
- Busca team-scoped por `trilhacode` retorna somente a API e o Mongo de staging; não há recurso frontend ou produção visível no projeto Coolify desta equipe.
- Uma navegação TLS autenticada pelo navegador até `https://api.staging.saitaro.tech/health` falhou com `ERR_CERT_AUTHORITY_INVALID`; nenhum aviso de segurança foi contornado. Assim, não há resposta HTTP validada de `/health` nem `/ready`.
- Uma consulta somente de manifesto ao digest privado GHCR feita com o contexto Docker existente na VPS falhou por autorização (erro sanitizado; sem login, pull ou exposição de credenciais). O pin atual não foi puxado nem executado.
- A lista team-scoped de nomes de variáveis do app API (runtime e preview) não contém chaves de SMTP, Resend ou remetente; valores não foram lidos. Entrega real de confirmação/recuperação por e-mail segue sem configuração operacional.
- G2 permanece bloqueado: imagem GHCR privada sem identidade de leitura; runner não implantado; usuário Mongo somente leitura não verificado; rede de staging atual sem `Internal` e attachable; backup/restore de banco não provados. O pin SSH do host está confirmado, mas uma identidade cliente autorizada não está disponível localmente.
- Recuperação da API, deploy, rede, credenciais, Mongo, G2 e serviços Dev Forge permaneceram intocados. Próxima ação segura: obter do operador a identificação do segundo membro/writer (ou acesso de leitura não sensível ao inventário Coolify correspondente) e um destino de backup de banco protegido; em paralelo, prover uma identidade SSH cliente autorizada ou manter inspeções pelo console web, sem expor chaves.
- CI #39114051802 do head `e0d1cb6aede8793404119bdbb78abed4de48a2fc` terminou `success`: backend, frontend, Compose e E2E aluno/admin aprovados; deploy de staging e produção `skipped`. É validação de código/documentação, não homologação operacional.

### Missão 15 — console Hostinger reaberto, Mongo e TLS (18/10/2026)

- A sessão Hostinger autenticada voltou a oferecer terminal root no host `srv2032201`. A listagem Docker foi somente leitura. O Mongo Trilha Code permanece `mongo:7`, saudável, sem porta publicada, com ID Docker completo verificado no host; o ID não é registrado neste log público. Os mounts persistentes continuam em `/data/configdb` e `/data/db`.
- A rede `trilhacode-staging-network` está em modo bridge com `Internal=false` e `Attachable=true`. O inventário mostrou dois endpoints: Mongo Trilha Code e `coolify-proxy`. O proxy é infraestrutura compartilhada e também participa de redes de outros projetos; nenhum endpoint foi conectado, removido ou alterado. Os containers de aplicação que apareceram na listagem Docker pertencem a outro projeto e não foram tocados.
- A consulta ao Mongo usou as variáveis de autenticação já existentes no container sem imprimir seus valores. `usersInfo` no banco `trilhacode_staging` confirmou `trilhacode_g2_ro` com papel `read`, `trilhacode_api` com `readWrite` e o usuário de inicialização `root` com escopo no mesmo banco. O exame de privilégios detalhados por ação não foi concluído; a atribuição do papel `read` foi observada. A API Trilha Code não tem container presente, portanto seu usuário `readWrite` não corresponde a um processo de aplicação ativo nesta inspeção. O proxy é o único peer além do Mongo e continua como componente compartilhado; não foi comprovado como escritor.
- Coolify continua registrando API `trilhacode-staging-api` sem container e com histórico de deploy vazio; branch configurada `main`, health check desabilitado e caminho `/`. Não existe frontend Trilha Code visível na lista de aplicações. A lista de backups Mongo segue vazia; os snapshots semanais Hostinger são da VPS inteira, não cópias isoladas do banco, e não foram usados.
- O DNS de `api.staging.saitaro.tech` resolve para o endereço público desta VPS. `curl` com validação TLS padrão recebeu `curl (60): SSL certificate problem: self-signed certificate`; nenhuma validação foi desabilitada. Não houve entrada correspondente ao hostname nos logs disponíveis do Traefik nas últimas 168 horas. A hipótese principal é que o domínio está recebendo o certificado padrão porque não há certificado ACME/roteador ativo para a API ausente; a causa ACME exata não foi comprovada.
- Nenhuma alteração de configuração, backup, restore, deploy, G2, rede ou banco foi executada. Nenhum segredo foi impresso. O Dev Forge e outros projetos ficaram intocados.
- G2 permanece bloqueado por: ausência de backup isolado com restore, rede G2 dedicada `Internal=true` inexistente, runner/manifesto não instalados, acesso GHCR/digest compatível não validado no host, e exame do escopo efetivo do usuário read-only ainda sem confirmação de ações. O papel Mongo `read` foi confirmado, mas não substitui os demais gates.
- Próxima ação executável depois de um destino externo de backup aprovado: capturar uma cópia consistente do Mongo, protegê-la fora do volume original e testar restore em MongoDB 7 descartável; então revisar a configuração de staging e preparar deploy com rollback. Para o certificado, recuperar primeiro API/router e validar ACME sem desabilitar TLS.
