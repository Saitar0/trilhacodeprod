# Trilha Code — Fase 2R.3: Candidato de release

## Escopo e decisão

Este documento registra a revisão local do working tree em 2026-10-16. Nenhum teste, deploy, push, migração ou acesso a banco foi executado nesta revisão. O commit deve ser preparado somente depois de confirmar a branch/base remota: o checkout está em `main`, mas seu upstream configurado é `origin/master`; o HEAD local (`91ff1424`) aparece 38 commits à frente desse upstream. Não promover nem publicar até esclarecer se esse histórico e destino são intencionais.

O candidato funcional aparenta conter a refatoração do backend para PyMongo Async, integridade/preflight e testes, os gates operacionais e o workflow de validação/publicação. O working tree **não está pronto para staging indiscriminado**: há ambiente virtual e bytecode rastreados com mudanças volumosas; mantenha-os fora do candidato e preserve-os no disco.

## Arquivos do candidato

Incluir as alterações de código, testes, workflow e documentação abaixo, após revisão do diff:

- CI e operação: `.github/workflows/ci-deploy.yml`, `DEPLOY.md`.
- Backend alterado: `backend/core.py`, `backend/indexes.py`, `backend/integrity.py`, `backend/learning.py`, `backend/manage.py`, `backend/migrations/0002_block_submission_capabilities.py`, `backend/migrations/__init__.py`, `backend/requirements.txt`, `backend/requirements.prod.txt`, `backend/ruff.toml`, `backend/routes_auth.py`, `backend/routes_content.py`, `backend/routes_import.py`, `backend/routes_progress.py`, `backend/routes_submissions.py`, `backend/routes_taxonomy.py`, `backend/routes_versions.py`, `backend/schemas/content.py`, `backend/seed.py`, `backend/server.py`.
- Backend services alterados: `backend/services/blocks.py`, `backend/services/common.py`, `backend/services/history.py`, `backend/services/imports.py`, `backend/services/nodes.py`, `backend/services/relations.py`, `backend/services/search.py`, `backend/services/stats.py`, `backend/services/submissions.py`, `backend/services/tracks.py`, `backend/services/versions.py`.
- Novos módulos: `backend/audit.py`, `backend/constants.py`, `backend/core_utils.py`, `backend/database.py`, `backend/permissions.py`, `backend/security.py`, `backend/serialization.py`, `backend/services/auth.py`, `backend/services/progress.py`, `backend/services/taxonomy.py`.
- Testes: `backend/tests/backend_test.py`, `backend/tests/conftest.py`, `backend/tests/test_core_modules.py`, `backend/tests/test_integrity_concurrency.py`, `backend/tests/test_pymongo_async.py`.
- Documentação de fase nova no working tree: `PHASE2A1_REFACTOR.md`, `PHASE2A2_REFACTOR.md`, `PHASE2A3_REFACTOR.md`, `PHASE2A4_INTEGRITY.md`, `PHASE2C1_ASYNC_FIX.md`, `PHASE2C_PYMONGO_ASYNC.md`, `PHASE2R1_QA_FIX.md`, `PHASE2_FINAL_REVIEW.md`, `PHASE2_QA_FINAL.md`, `PHASE2_RELEASE_READINESS.md` e este arquivo.

Os manifests frontend (`frontend/package.json`, `frontend/package-lock.json`), Dockerfiles, `compose.yaml`, exemplos de ambiente, scripts e demais fontes frontend estão presentes e sem alteração reportada no working tree. Incluí-los no commit apenas se o diff completo mostrar uma mudança necessária; não há alteração frontend nesta revisão.

## Classificação do estado local

- **Alterados intencionais:** workflow de deploy, documentação de deploy, módulos backend de arquitetura/serviços/integridade, inicialização e migração, dependências/configuração Ruff e testes.
- **Novos intencionais:** os novos módulos backend, os três novos testes, os relatórios das fases listados acima.
- **Alterações locais que não pertencem ao release:** arquivos sob `backend/.venv311/` (pacotes instalados, inclusive PyMongo 4.18.2) e `backend/tests/__pycache__/backend_test.cpython-311-pytest-9.1.1.pyc`. O virtualenv foi rastreado historicamente; há mudanças, exclusões e adições em `site-packages`. Não apague, restaure nem faça stage desses arquivos como parte deste candidato. Regras de ignore não removem arquivos já rastreados.
- **Não rastrear:** ambientes `.venv`/`venv`, `node_modules`, `.pytest_cache`, `.ruff_cache`, `__pycache__`/`.pyc`, build `frontend/dist`, logs (incluindo `mongo.log`), `mongo-data`, arquivos `.env` locais e dados de teste/backup. Os exemplos `.env.example`, `.env.staging.example` e `.env.production.example` são templates versionáveis, não credenciais. O backup `docs/courses/trilhacode/trilha-code-bulk-import.backup-before-block-split-20261015.json` é dado local, não artefato de release. Pastas `.antigravity`, `memory` e `test_reports` são locais/geradas e não devem ser incluídas sem revisão específica.

O status mostrou os arquivos locais citados como ignorados/não candidatos e não reportou `.env` real entre os não rastreados. Não se deve abrir ou copiar conteúdo de segredo para o commit. `.gitignore` e `backend/.dockerignore` (ou regras equivalentes do contexto Docker) precisam continuar excluindo esses artefatos; ignore não neutraliza rastreamento anterior.

## Revisões e integridade

- **Preflight incluído:** `backend/indexes.py` e `backend/manage.py` implementam o comando de leitura `preflight-indexes`. O teste corrigido faz parte das alterações novas em `backend/tests/test_integrity_concurrency.py`: `test_unique_index_preflight_reports_duplicates_and_respects_partial_indexes` exercita duplicatas e índices parciais; o mesmo arquivo testa que o comando falha em duplicatas/conflitos. Portanto, esse arquivo deve integrar o candidato.
- **Cobertura de artefatos:** os novos módulos importados pela aplicação estão presentes; os testes incluem `conftest.py` e módulos de teste; `backend/requirements-dev.txt`, `backend/Dockerfile.prod`, `frontend/Dockerfile.prod`, manifests frontend e `frontend/package-lock.json` existem. O workflow referencia requisitos, testes, compilação e builds existentes. Migrações `0001` e `0002` e os documentos operacionais estão presentes.
- **Dependências Python:** `requirements.txt` e `requirements.prod.txt` removem Motor e mantêm PyMongo 4.18.2; o Dockerfile de produção instala o manifest de produção. Não há lockfile Python dedicado, e `sentry-sdk[fastapi]>=2.0,<3` permite resolver versões diferentes ao longo do tempo, portanto a imagem não é totalmente reproduzível apesar de várias dependências fixadas. O CI deve validar a resolução real no commit candidato.
- **Frontend:** `package.json` e `package-lock.json` estão presentes e o workflow usa `npm ci`, que verifica consistência do lockfile. Nenhuma alteração desses arquivos aparece no working tree revisado; não foi feita instalação nem auditoria nesta revisão.
- **Alterações acidentais:** não identifiquei arquivo funcional frontend modificado; há mudança grande e claramente local no virtualenv e bytecode. O diff completo de código permanece obrigatório no momento do stage; não usar `git add -A` ou `git add .`.
- **Base Git:** além da discrepância `main` → `origin/master` e 38 commits à frente, não foi confirmada neste trabalho a branch remota de release nem se o histórico local contém apenas mudanças aprovadas. Revise o log/base e a política de branch antes de criar o commit.

## CI e deploy

O workflow `.github/workflows/ci-deploy.yml` agora executa validação em `push`/`pull_request` para `main` e `staging`, e oferece `workflow_dispatch` com `deploy_target=none` por padrão. Os jobs `deploy-staging` e `deploy-production` exigem evento `workflow_dispatch`, input explícito correspondente, branch exata (`staging` ou `main`) e sucesso dos jobs backend/frontend. Portanto, **um push de validação não satisfaz as condições de deploy deste workflow GitHub Actions**. O dispatch `none` também não atende às condições de publicação.

Isso não prova que o push seja inofensivo no Coolify: confirmar externamente que o auto-deploy por push está desativado para cada aplicação, ou configurado para aguardar CI. Confirmar também que os GitHub Environments `staging` e `production` existem, têm secrets corretos e revisores/aprovação obrigatória; declarar `environment:` no YAML, por si só, não cria essas proteções. Proteger branches com checks obrigatórios e confirmar tokens/webhooks mínimos são pendências externas. Nenhuma dessas configurações foi inspecionada ou modificada.

## Evidências locais de validação

- Evidência fornecida pelo usuário no contexto: 63 testes backend aprovados e teste específico do preflight aprovado em PowerShell externo.
- Evidência de etapa anterior registrada nos relatórios: Ruff e compilação Python aprovados; frontend anteriormente passou `npm ci`, typecheck, ESLint, Vitest, build e `npm audit`.
- Nesta revisão foram executados `git status`, `git diff --stat`, `git diff`, `git ls-files --others --exclude-standard`, buscas/leituras estáticas do workflow, manifests, Dockerfiles, documentação e testes. Não executei testes nem builds; não acessei bancos.
- Essas evidências locais/históricas não substituem checks verdes no commit exato. Guardar a URL e os logs de todos os jobs CI associados ao SHA do candidato, incluindo Ruff, backend, compilação, auditoria Python, build Docker, frontend e auditoria npm.

## Procedimento seguro para preparar o commit

1. Confirmar a branch/base de release e reconciliar a divergência do upstream. Preservar qualquer alteração local e manter backup normal do working tree antes de operações de branch; não resetar, limpar ou restaurar arquivos em massa.
2. Revisar o diff por arquivo funcional e abrir os relatórios de fase. Confirmar se todos são documentação final desejada. Verificar `git status --short`, `git diff --check`, `git diff --stat` e o diff completo imediatamente antes de preparar.
3. Preparar o índice apenas com os caminhos de candidato listados acima, em grupos explícitos e seletivos. Não usar `git add -A`, `git add .` nem adicionar `backend/.venv311/`, `backend/tests/__pycache__/`, arquivos `.env`, logs, caches, banco local ou backup JSON. Usar stage interativo para arquivos alterados quando necessário.
4. Inspecionar `git diff --cached --stat` e `git diff --cached` por completo. Confirmar que `backend/tests/test_integrity_concurrency.py` e o teste corrigido estão staged, que nenhum artefato local/segredo aparece e que arquivos preexistentes fora do candidato continuam preservados.
5. Criar o commit somente depois dessa revisão manual; registrar SHA e branch. Não executar push/deploy até aprovação operacional e CI verde desse SHA.

Os comandos abaixo são sugestões para o responsável executar depois da confirmação da branch; não foram executados nesta revisão:

```powershell
git status --short --branch
git diff --check
git diff --stat
git diff
# Adicionar apenas os caminhos aprovados da seção “Arquivos do candidato”, em grupos explícitos.
git diff --cached --check
git diff --cached --stat
git diff --cached
# Após validar o índice:
git commit -m "feat: consolidate phase 2 release candidate"
```

## CI sem deploy

- Opção preferida após o commit e push autorizado à branch correta: executar `workflow_dispatch` na branch/SHA candidato com `deploy_target=none`; ou abrir PR para `main`/`staging`. Push/PR executa validação sem deploy pelo GitHub Actions. A execução manual não foi disparada.
- Exemplo de disparo manual pelo GitHub CLI, **não executado**: `gh workflow run ci-deploy.yml --ref <branch-candidata> -f deploy_target=none`.
- Antes de qualquer push, confirmar o auto-deploy no Coolify: uma configuração de push independente pode publicar mesmo quando os jobs de deploy do GitHub não são elegíveis.
- Exigir jobs backend e frontend verdes no SHA exato: Ruff, testes backend com Mongo de CI isolado, compilação, teste de configuração insegura, build/auditoria Python e frontend `npm ci`, typecheck, lint, Vitest, build e `npm audit`.

## Pendências, riscos e avanço para staging

1. **Bloqueio de release:** confirmar se `main` acompanhando `origin/master` e estando 38 commits à frente é intencional; estabelecer a branch/base e o destino de PR/push corretos.
2. Confirmar no Coolify que auto-deploy por push está desligado (ou aguarda checks) para as aplicações de staging e production. Confirmar as configurações externas de branches, domains, secrets, tokens, webhooks e GitHub Environments/revisores sem expor valores secretos.
3. Validar o candidato seletivo: nenhum venv/bytecode/dado local, segredo ou backup deve estar no índice. Arquivos do ambiente virtual já rastreados são um problema histórico separado; não tentar removê-los neste commit sem mudança planejada.
4. Obter CI verde no SHA exato e guardar evidência verificável. Resolver a falta de lock Python se reprodução estrita for requisito do release.
5. Staging somente quando branch/base e aprovação de release estiverem confirmadas; CI do SHA estiver verde; ambiente e Mongo staging forem isolados; backup e restore de teste estiverem confirmados; owner, janela, rollback, espaço/recursos e freeze de escritas estiverem acordados.
6. Em staging, com autorização do operador, rodar preflight, migration, preflight pós-migração, ensure-indexes e preflight final conforme `DEPLOY.md`; registrar tempo, métricas, schema 2 e todos os índices `OK`. Fazer deploy de staging pelo gate aprovado e validar `/health`, `/ready`, smoke tests, logs e checklist visual desktop/mobile.
7. Não avançar a production até homologação visual e operacional em staging, evidência de backup/restore, métricas aceitáveis, aprovação manual configurada, rollback ensaiado e decisão explícita do responsável.

Nenhuma conexão a bancos existentes, migração ou alteração de dados foi feita.
