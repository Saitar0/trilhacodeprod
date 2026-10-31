# Auditoria técnica — rodada 2 (2026-10-31)

> **PARCIAL — NÃO É APROVAÇÃO TÉCNICA.** Somente leitura de GitHub API/raw; nenhum código executado. FATO, INFERÊNCIA e NÃO SEI indicam níveis de evidência.

## 1. Metadados e limites
**FATO:** main: `22dca64556338a8fa9aaa89ce627a4f4af72317d` ([API](https://api.github.com/repos/Saitar0/trilhacodeprod/branches/main)). Sem clone, Docker, deploy, secrets ou bancos. Git/Python locais disponíveis; gh e Docker indisponíveis. **NÃO SEI:** limite de rate API e causas de endpoints sem resposta legível.

## 2. Resumo executivo — rodada 3
**FATO:** main `22dca64556338a8fa9aaa89ce627a4f4af72317d` e heads #38/#39/#40/#43/#44 reconfirmados por API. **FATO:** `ci-deploy.yml` só dispara PR contra main/staging, portanto não executa automaticamente para bases intermediárias de #39/#43. **FATO:** #43 tem Beta 6.1 verde, mas não suíte foundation completa. **FATO:** run main 41074693439 falhou por caminho pytest inexistente e cinco testes Playwright falhos; PR #44 falhou em audits de dependências. **FATO:** pacote curricular JSON tem 10 fases, 53 módulos, 131 unidades, 26.190 minutos. **INFERÊNCIA:** H1, gate histórico de hash ausente no workflow Beta 6.1 do #43, explica CI verde versus Issue #42. Não é aprovação de merge.

## 3. Baseline e divergências
| Ref | Head SHA completo | Base SHA completo | Estado/draft | Mergeable state | Commits | Arquivos | +/- |
|---|---|---|---|---|---:|---:|---:|
| main | `22dca64556338a8fa9aaa89ce627a4f4af72317d` | — | branch | — | — | — | — |
| [#38](https://github.com/Saitar0/trilhacodeprod/pull/38) | `86cf85e6af6edf83b9c9f78ed6d3aef80e4ca089` | `22dca64556338a8fa9aaa89ce627a4f4af72317d` | open/não | clean | 5 | 7 | +178/-25 |
| [#39](https://github.com/Saitar0/trilhacodeprod/pull/39) | `4df2c4ec5b12f374b18caf6fab19d193be9c77c8` | `86cf85e6af6edf83b9c9f78ed6d3aef80e4ca089` | open/não | clean | 5 | 13 | +1058/-0 |
| [#40](https://github.com/Saitar0/trilhacodeprod/pull/40) | `401e0b8c1f20fadaaf15d0436df0d7a8c513b33f` | `86cf85e6af6edf83b9c9f78ed6d3aef80e4ca089` | open/não | clean | 77 | 382 | +59516/-423 |
| [#43](https://github.com/Saitar0/trilhacodeprod/pull/43) | `2383364a35e85c15a79904ee0af7f71d626ac646` | `4df2c4ec5b12f374b18caf6fab19d193be9c77c8` | open/não | clean | 19 | 106 | +9281/-423 |

**FATO:** [compare main...#43](https://api.github.com/repos/Saitar0/trilhacodeprod/compare/22dca64556338a8fa9aaa89ce627a4f4af72317d...2383364a35e85c15a79904ee0af7f71d626ac646) retornou 124 arquivos, +10517/-448.

## 4. Workflows e checks por SHA — rodada 3
**FATO:** cinco workflows na main `22dca64556338a8fa9aaa89ce627a4f4af72317d` e seis no #43 `2383364a35e85c15a79904ee0af7f71d626ac646` foram lidos integralmente por raw/API. Blocos `on:` (nenhum usa branches-ignore ou paths-ignore):
- `.github/workflows/ci-deploy.yml`, [main linhas 3–18](https://github.com/Saitar0/trilhacodeprod/blob/22dca64556338a8fa9aaa89ce627a4f4af72317d/.github/workflows/ci-deploy.yml#L3-L18) e [#43 linhas 3–18](https://github.com/Saitar0/trilhacodeprod/blob/2383364a35e85c15a79904ee0af7f71d626ac646/.github/workflows/ci-deploy.yml#L3-L18): `push: branches: [main, staging]`; `pull_request: branches: [main, staging]`; `workflow_dispatch` com `deploy_target`. `permissions: contents: read`. Jobs de deploy exigem workflow_dispatch e branch específica, [linhas 228–257](https://github.com/Saitar0/trilhacodeprod/blob/2383364a35e85c15a79904ee0af7f71d626ac646/.github/workflows/ci-deploy.yml#L228-L257).
- `.github/workflows/foundation-validation.yml`, [main](https://github.com/Saitar0/trilhacodeprod/blob/22dca64556338a8fa9aaa89ce627a4f4af72317d/.github/workflows/foundation-validation.yml#L3-L7) e [#43](https://github.com/Saitar0/trilhacodeprod/blob/2383364a35e85c15a79904ee0af7f71d626ac646/.github/workflows/foundation-validation.yml#L3-L7): `workflow_dispatch:`, `permissions: contents: read`.
- `.github/workflows/g2-manual-backend-build.yml`, [main](https://github.com/Saitar0/trilhacodeprod/blob/22dca64556338a8fa9aaa89ce627a4f4af72317d/.github/workflows/g2-manual-backend-build.yml#L3-L7), [#43](https://github.com/Saitar0/trilhacodeprod/blob/2383364a35e85c15a79904ee0af7f71d626ac646/.github/workflows/g2-manual-backend-build.yml#L3-L7): `workflow_dispatch:`, `permissions: contents: read`.
- `.github/workflows/g2-publish-backend-ghcr.yml`, [main](https://github.com/Saitar0/trilhacodeprod/blob/22dca64556338a8fa9aaa89ce627a4f4af72317d/.github/workflows/g2-publish-backend-ghcr.yml#L3-L9), [#43](https://github.com/Saitar0/trilhacodeprod/blob/2383364a35e85c15a79904ee0af7f71d626ac646/.github/workflows/g2-publish-backend-ghcr.yml#L3-L9): `workflow_dispatch:`, `permissions: contents: read, packages: write`; GHCR push apenas manual.
- `.github/workflows/g2-staging-preflight.yml`, [main](https://github.com/Saitar0/trilhacodeprod/blob/22dca64556338a8fa9aaa89ce627a4f4af72317d/.github/workflows/g2-staging-preflight.yml#L3-L7), [#43](https://github.com/Saitar0/trilhacodeprod/blob/2383364a35e85c15a79904ee0af7f71d626ac646/.github/workflows/g2-staging-preflight.yml#L3-L7): `workflow_dispatch:`, `permissions: {}`; SSH apenas manual.
- `.github/workflows/beta61-validation.yml` só #43, [linhas 3–11](https://github.com/Saitar0/trilhacodeprod/blob/2383364a35e85c15a79904ee0af7f71d626ac646/.github/workflows/beta61-validation.yml#L3-L11): `workflow_dispatch:` e `pull_request: paths: [.github/workflows/beta61-validation.yml, backend/**, frontend/**, compose.qa.yaml, ops/editorial-generations/requirements.lock]`, sem filtro branches; `permissions: contents: read`. Nenhum `pull_request_target` ou `workflow_run` nos arquivos.

**FATO:** `pull_request.branches` filtra base: #39 e #43 não disparam ci-deploy pois suas bases são #38 e #39. Beta 6.1 aceita PR contra qualquer base com paths selecionados. Nenhum push abrange branches #39/#43.

**FATO:** GET `/actions/runs?head_sha=...&per_page=100` e `/commits/.../check-runs?per_page=100`:
| Head SHA | Runs (workflow; evento; branch; conclusão) | Check-runs |
|---|---|---|
| `86cf85e6af6edf83b9c9f78ed6d3aef80e4ca089` | [41081083098](https://github.com/Saitar0/trilhacodeprod/actions/runs/41081083098) CI and Coolify deploy; pull_request; codex/foundation-ci-e2e-recovery; success. [41081073931](https://github.com/Saitar0/trilhacodeprod/actions/runs/41081073931) foundation; workflow_dispatch; mesma branch; success | 9 success, 2 skipped |
| `4df2c4ec5b12f374b18caf6fab19d193be9c77c8` | [41084556090](https://github.com/Saitar0/trilhacodeprod/actions/runs/41084556090) foundation; workflow_dispatch; codex/beta5-contracts-integration-wave1; success | 5 success |
| `2383364a35e85c15a79904ee0af7f71d626ac646` | [41121493327](https://github.com/Saitar0/trilhacodeprod/actions/runs/41121493327) Beta 6.1; pull_request; codex/beta6-1-http-chromium-clean-pr39; success | 1 success |
| `476ae94a2c41ff653360e72d944d510147c3bead` | [41169866007](https://github.com/Saitar0/trilhacodeprod/actions/runs/41169866007) CI and Coolify deploy; pull_request; audit/baseline-verificacao-2026-10-31; failure | backend/frontend failure, e2e/compose success, deploys skipped |

**FATO:** [run 41121493327](https://github.com/Saitar0/trilhacodeprod/actions/runs/41121493327): único job Beta 6.1 HTTP and Chromium, success, comando `PYTHONPATH=. python test_support/run_beta6_1_journey.py`. **INFERÊNCIA:** não é suíte foundation completa.

**FATO:** [run 41074693439](https://github.com/Saitar0/trilhacodeprod/actions/runs/41074693439), evento workflow_dispatch: Backend and MongoDB 7 success; Frontend on Node 20 success; Docker and G2 contracts failure; Integrated E2E with synthetic data failure; Homologation summary failure. [Log Docker/G2](https://github.com/Saitar0/trilhacodeprod/actions/runs/41074693439/job/124127642686): mongo:7 baixado com sucesso; pytest `ERROR: file or directory not found: unit_tests/test_compose_qa_isolation.py`, exit code 4. [Log E2E](https://github.com/Saitar0/trilhacodeprod/actions/runs/41074693439/job/124127642065): 5 failed, timeouts `locator.fill` e `expect(locator).toBeVisible()`. Causa raiz adicional: NÃO SEI.

**FATO:** [run 41169866007](https://github.com/Saitar0/trilhacodeprod/actions/runs/41169866007) PR #44: backend falhou em `pip-audit -r backend/requirements.prod.txt`; frontend em `npm audit --audit-level=high`; E2E/compose passaram; deploys skipped. Não são os mesmos jobs vermelhos da foundation. Checks do novo commit: NÃO SEI até conclusão.

## 5. Missão 4
**FATO:** [branches paginadas](https://api.github.com/repos/Saitar0/trilhacodeprod/branches?per_page=100&page=1): 100+9+0 entradas nas páginas 1,2,3. [PRs](https://api.github.com/repos/Saitar0/trilhacodeprod/pulls?state=all&per_page=100&page=1): 43 entradas. [Releases](https://api.github.com/repos/Saitar0/trilhacodeprod/releases?per_page=100): zero. **NÃO SEI:** implementação da Missão 4; buscas por termos em todas as branches/commits/código/tags/forks/runs não foram exauridas. Documentação ou mocks não são evidência de implementação. Ausência no GitHub não comprova ausência local.

## 6. Mapa de risco #43
**FATO:** [compare #39...#43](https://api.github.com/repos/Saitar0/trilhacodeprod/compare/4df2c4ec5b12f374b18caf6fab19d193be9c77c8...2383364a35e85c15a79904ee0af7f71d626ac646). Agrupamentos por nome de arquivo são sobrepostos:
| Área | Arquivos | +/- | Risco (INFERÊNCIA) | Pergunta |
|---|---:|---:|---|---|
| Workflows | 2 | +66/-2 | Médio | A suíte foundation também será exigida? |
| Auth, security, sessions, permissions | 10 | +686/-28 | Alto | Todas as rotas mutantes validam autenticação e autorização? |
| Import, indexes, integrity | 9 | +1158/-109 | Alto | Há idempotência e proteção contra concorrência? |
| Testes/harness/fixtures | 38 | +4461/-67 | Alto | Há isolamento e cleanup estritamente delimitados? |
| Frontend | 33 | +1911/-94 | Médio | Erros, sessão e permissões permanecem coerentes? |
| Docs | 11 | +317/-0 | Baixo | Relatos distinguem observação de hipótese? |

**NÃO SEI:** patches de alto risco não foram integralmente auditados, nem os 17 writers inventariados; não declarar ausência de vulnerabilidades.

## 7. Proveniência curricular e Issues #41/#42 — rodada 3
**FATO:** árvores Git por API completas nos refs main `22dca64556338a8fa9aaa89ce627a4f4af72317d`, #39 `4df2c4ec5b12f374b18caf6fab19d193be9c77c8`, #43 `2383364a35e85c15a79904ee0af7f71d626ac646`, #40 `401e0b8c1f20fadaaf15d0436df0d7a8c513b33f`. Em todos: `docs/courses/trilhacode/trilha-code-bulk-import.json` blob `9895e7c1ad200da3d8bd5691efce61267697f8ed`, 2.154.114 bytes; `docs/courses/trilhacode/Conteudos/Fase_1/1.1_Computacao_e_software.md` blob `5b7687c85b351a9878a3017dec226b647d8d6ae5`, 18.367 bytes; 143 entradas (diretórios e arquivos) sob `Conteudos/` em cada árvore. [main](https://api.github.com/repos/Saitar0/trilhacodeprod/git/trees/22dca64556338a8fa9aaa89ce627a4f4af72317d?recursive=1), [#39](https://api.github.com/repos/Saitar0/trilhacodeprod/git/trees/4df2c4ec5b12f374b18caf6fab19d193be9c77c8?recursive=1), [#43](https://api.github.com/repos/Saitar0/trilhacodeprod/git/trees/2383364a35e85c15a79904ee0af7f71d626ac646?recursive=1), [#40](https://api.github.com/repos/Saitar0/trilhacodeprod/git/trees/401e0b8c1f20fadaaf15d0436df0d7a8c513b33f?recursive=1).

**FATO — diagnóstico, não correção:** blob JSON lido e interpretado em memória via GitHub API: 10 phase, 53 module, 131 submodule, soma estimated_minutes 26.190, 194 refs únicos de 194 encontrados. Representação UTF-8 devolvida contém 18.453 LF e 0 CRLF; **NÃO SEI** se o conector preserva bytes raw, logo SHA-256 independente e EOL byte-a-byte não verificados. `.gitattributes` ausente nos quatro trees; config Git local NÃO SEI. [Blob](https://api.github.com/repos/Saitar0/trilhacodeprod/git/blobs/9895e7c1ad200da3d8bd5691efce61267697f8ed).

**FATO:** fixture `backend/integration_tests/fixtures/beta2/unit_1_1_computacao_e_software.source.md` blob `5b7687c85b351a9878a3017dec226b647d8d6ae5`, 18.367 bytes, e teste `backend/unit_tests/test_beta_curriculum_fidelity.py` blob `2d7ec509ff27d134114ba255f5fc02da12b56dba`, 10.379 bytes, existem no #40, mas não nos trees main/#39/#43. [Teste #40 linhas 31–43 e 212–213](https://github.com/Saitar0/trilhacodeprod/blob/401e0b8c1f20fadaaf15d0436df0d7a8c513b33f/backend/unit_tests/test_beta_curriculum_fidelity.py#L31-L43) exige hash bruto `db6e3ae5bcbdfa786caae171897f5140fc167249f591cb5ed9fcf9d1dd3aeec4`; registra hash LF `21736a209b840406169d88862f793e848952a402a01a37ae22d974d7bd59e513`. [Conversor #40 linhas 420–436](https://github.com/Saitar0/trilhacodeprod/blob/401e0b8c1f20fadaaf15d0436df0d7a8c513b33f/backend/curriculum_contract/experimental_beta_curriculum_fidelity.py#L420-L436) rejeita divergência.

**INFERÊNCIA — H1 selecionada:** o gate histórico não roda no [Beta 6.1 do #43](https://github.com/Saitar0/trilhacodeprod/blob/2383364a35e85c15a79904ee0af7f71d626ac646/.github/workflows/beta61-validation.yml#L26-L52) e os arquivos de teste/fixture não constam do #43; tampouco o teste existe no #43 para o ci-deploy. H2 (outro artefato) não explica ausência do gate; H3 (normalização EOL antes da comparação) contraria comparação explícita de hash bruto no teste #40; H4 (issue superada) não tem evidência e Issue #42 está aberta. CI verde do #43 não valida proveniência histórica.

**FATO:** [Issue #42](https://github.com/Saitar0/trilhacodeprod/issues/42) aberta, zero comentários: hash esperado vs LF divergentes; relato de que CRLF reproduz hash esperado. **INFERÊNCIA:** deriva EOL é causa provável, não comprovada independentemente. Opções não aplicadas: restaurar bytes CRLF aprovados (mantém hash, exige fonte confiável); rebaseline manifesto/hash em LF com autorização humana (padroniza, muda contrato); .gitattributes (previne deriva, exige avaliação de checkout). [Issue #41](https://github.com/Saitar0/trilhacodeprod/issues/41) aberta, zero comentários: `docker run --pull never mongo:7` requer imagem previamente provisionada; o run 41074693439 baixou a imagem e falhou depois por caminho de teste ausente.

## 8. Execução de testes
**NÃO EXECUTADO:** por proibição expressa de clone, Docker e execução de código do repositório; não há Mongo descartável comprovado. Alegação de 47 testes: **NÃO SEI**.

## 9. Achados priorizados
1. **FATO/Alto:** CI mais recente da main falhou em Docker/G2 e E2E: [run](https://github.com/Saitar0/trilhacodeprod/actions/runs/41074693439).
2. **INFERÊNCIA/Alto:** CI verde do #43 é especializado e não prova homologação completa: [workflow](https://github.com/Saitar0/trilhacodeprod/blob/2383364a35e85c15a79904ee0af7f71d626ac646/.github/workflows/beta61-validation.yml).
3. **FATO/Médio:** decisão de proveniência curricular pendente: [Issue #42](https://github.com/Saitar0/trilhacodeprod/issues/42).

## 10. Não verificado — rodada 3
**NÃO SEI:** SHA-256 calculado independentemente sobre bytes raw, EOL real da fixture, referências órfãs, configuração Git EOL fora do tree, causa raiz dos timeouts E2E, vulnerabilidades específicas de pip-audit/npm audit, regras obrigatórias de proteção da main e resultados dos checks do novo commit. Sem clone/Docker/execução de código. Endpoint `GET /branches/audit%2Fbaseline-verificacao-2026-10-31` retornou HTTP 400 INVALID_ARGUMENT do conector; branch confirmada via listagem `GET /branches?per_page=100&page=1` e PR #44.

## 11. Anexo de consultas e decisão de publicação — rodada 3
**FATO:** GET `/branches/main`, `/branches?per_page=100&page=1`, `/pulls/{38,39,40,43,44}`, `/contents/.github/workflows?ref={main,#43}`, raw de 11 workflows, `/actions/runs?head_sha={#38,#39,#43,#44}&per_page=100`, `/commits/{SHA}/check-runs?per_page=100`, `/commits/{SHA}/status`, `/actions/runs/{41121493327,41074693439,41169866007}/jobs?per_page=100`, logs dos jobs `124127642065`, `124127642686`, `124445289047`, `124445288785`; `/git/trees/{main,#39,#40,#43}?recursive=1`, `/git/blobs/9895e7c1ad200da3d8bd5691efce61267697f8ed`, leitura do teste e conversor no #40, `/issues/{41,42}/comments`. Data de referência 2026-10-31, horário exato das consultas NÃO SEI. GET `/branches/audit%2Fbaseline-verificacao-2026-10-31`: 400 INVALID_ARGUMENT, sem contorno.

**FATO:** antes do commit, branch audit conferida em listagem no head `476ae94a2c41ff653360e72d944d510147c3bead`. Avaliação de risco: [ci-deploy.yml main, linhas 3–18 e 226–257](https://github.com/Saitar0/trilhacodeprod/blob/22dca64556338a8fa9aaa89ce627a4f4af72317d/.github/workflows/ci-deploy.yml) confirma PR para main dispara build/test/lint e audits, sem deploy, secrets em jobs PR ou push de imagem; deploys exigem dispatch. Commit único restrito a este documento, sem alterar gates. Resultado dos novos checks deve ser observado, jamais alterado.

