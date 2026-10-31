# Auditoria técnica — rodada 2 (2026-10-31)

> **PARCIAL — NÃO É APROVAÇÃO TÉCNICA.** Somente leitura de GitHub API/raw; nenhum código executado. FATO, INFERÊNCIA e NÃO SEI indicam níveis de evidência.

## 1. Metadados e limites
**FATO:** main: `22dca64556338a8fa9aaa89ce627a4f4af72317d` ([API](https://api.github.com/repos/Saitar0/trilhacodeprod/branches/main)). Sem clone, Docker, deploy, secrets ou bancos. Git/Python locais disponíveis; gh e Docker indisponíveis. **NÃO SEI:** limite de rate API e causas de endpoints sem resposta legível.

## 2. Resumo executivo
**FATO:** cadeia #38 → #39 → #43 confirmada; #40 fora dela. **FATO:** diff acumulado main...#43 tem 124 arquivos, +10.517/-448; delta contra #39 tem 106, +9.281/-423. **FATO:** CI mais recente da main falhou; CI específico do #43 passou. **INFERÊNCIA:** check especializado não basta para homologação completa.

## 3. Baseline e divergências
| Ref | Head SHA completo | Base SHA completo | Estado/draft | Mergeable state | Commits | Arquivos | +/- |
|---|---|---|---|---|---:|---:|---:|
| main | `22dca64556338a8fa9aaa89ce627a4f4af72317d` | — | branch | — | — | — | — |
| [#38](https://github.com/Saitar0/trilhacodeprod/pull/38) | `86cf85e6af6edf83b9c9f78ed6d3aef80e4ca089` | `22dca64556338a8fa9aaa89ce627a4f4af72317d` | open/não | clean | 5 | 7 | +178/-25 |
| [#39](https://github.com/Saitar0/trilhacodeprod/pull/39) | `4df2c4ec5b12f374b18caf6fab19d193be9c77c8` | `86cf85e6af6edf83b9c9f78ed6d3aef80e4ca089` | open/não | clean | 5 | 13 | +1058/-0 |
| [#40](https://github.com/Saitar0/trilhacodeprod/pull/40) | `401e0b8c1f20fadaaf15d0436df0d7a8c513b33f` | `86cf85e6af6edf83b9c9f78ed6d3aef80e4ca089` | open/não | clean | 77 | 382 | +59516/-423 |
| [#43](https://github.com/Saitar0/trilhacodeprod/pull/43) | `2383364a35e85c15a79904ee0af7f71d626ac646` | `4df2c4ec5b12f374b18caf6fab19d193be9c77c8` | open/não | clean | 19 | 106 | +9281/-423 |

**FATO:** [compare main...#43](https://api.github.com/repos/Saitar0/trilhacodeprod/compare/22dca64556338a8fa9aaa89ce627a4f4af72317d...2383364a35e85c15a79904ee0af7f71d626ac646) retornou 124 arquivos, +10517/-448.

## 4. Workflows e checks por SHA
**FATO:** cinco workflows da main e seis no #43 foram lidos. [ci-deploy.yml na main](https://github.com/Saitar0/trilhacodeprod/blob/22dca64556338a8fa9aaa89ce627a4f4af72317d/.github/workflows/ci-deploy.yml#L3-L18) define push apenas em main/staging, PR para main/staging, permissions contents:read. Os jobs de deploy [linhas 226–257](https://github.com/Saitar0/trilhacodeprod/blob/22dca64556338a8fa9aaa89ce627a4f4af72317d/.github/workflows/ci-deploy.yml#L226-L257) exigem workflow_dispatch e branch/target específicos; não executam por PR. Os quatro outros workflows da main são exclusivamente manuais. No #43, [beta61-validation.yml](https://github.com/Saitar0/trilhacodeprod/blob/2383364a35e85c15a79904ee0af7f71d626ac646/.github/workflows/beta61-validation.yml#L3-L62) dispara por PR apenas quando mudam caminhos selecionados (backend/frontend/compose/lock/workflow), sem gatilho push. Não foram encontrados pull_request_target nem workflow_run nesses arquivos.

**FATO:** Checks por SHA (GET /commits/{sha}/check-runs?per_page=100):
- main `22dca64556338a8fa9aaa89ce627a4f4af72317d`: [41074693439](https://github.com/Saitar0/trilhacodeprod/actions/runs/41074693439) failure; backend/frontend success; Docker/G2, E2E e summary failure. Run anterior [40488544210](https://github.com/Saitar0/trilhacodeprod/actions/runs/40488544210) success, deploys skipped.
- #38 `86cf85e6af6edf83b9c9f78ed6d3aef80e4ca089`: [41081073931](https://github.com/Saitar0/trilhacodeprod/actions/runs/41081073931) e [41081083098](https://github.com/Saitar0/trilhacodeprod/actions/runs/41081083098), checks success, deploys skipped.
- #39 `4df2c4ec5b12f374b18caf6fab19d193be9c77c8`: [41084556090](https://github.com/Saitar0/trilhacodeprod/actions/runs/41084556090), backend/frontend/Docker/E2E/summary success.
- #40 `401e0b8c1f20fadaaf15d0436df0d7a8c513b33f`: [41118102821](https://github.com/Saitar0/trilhacodeprod/actions/runs/41118102821), Beta 6.1 success.
- #43 `2383364a35e85c15a79904ee0af7f71d626ac646`: [41121493327](https://github.com/Saitar0/trilhacodeprod/actions/runs/41121493327), Beta 6.1 success.

**FATO:** Job único do #43 executa `PYTHONPATH=. python test_support/run_beta6_1_journey.py` após instalação de requirements-dev e verificação do Docker; **INFERÊNCIA:** subconjunto, não suíte completa. **NÃO SEI:** causas detalhadas das falhas na main, proteção obrigatória de branch e reviews completos; endpoint /branches/main/protection não retornou resultado legível. **FATO:** [AGENTS.md](https://github.com/Saitar0/trilhacodeprod/blob/22dca64556338a8fa9aaa89ce627a4f4af72317d/AGENTS.md) foi lido. CONTRIBUTING e CODEOWNERS: **NÃO SEI**.

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

## 7. Proveniência curricular e Issues
**FATO:** `docs/courses/trilhacode/trilha-code-bulk-import.json` é o mesmo blob Git `9895e7c1ad200da3d8bd5691efce61267697f8ed` (2.154.114 bytes) na [main](https://api.github.com/repos/Saitar0/trilhacodeprod/git/trees/22dca64556338a8fa9aaa89ce627a4f4af72317d?recursive=1) e no [#43](https://api.github.com/repos/Saitar0/trilhacodeprod/git/trees/2383364a35e85c15a79904ee0af7f71d626ac646?recursive=1). **NÃO SEI:** SHA-256 em bytes, CRLF/LF, schema, contagem de fases/módulos/unidades/minutos e referências órfãs; não calculados.

**FATO:** [Issue #42](https://github.com/Saitar0/trilhacodeprod/issues/42) aberta, sem comentários, relata SHA-256 esperado `db6e3ae5bcbdfa786caae171897f5140fc167249f591cb5ed9fcf9d1dd3aeec4` versus atual `21736a209b840406169d88862f793e848952a402a01a37ae22d974d7bd59e513`; relato atribui diferença a CRLF/LF. **INFERÊNCIA:** EOL é hipótese forte, não reprodução independente. Opções não aplicadas: restaurar CRLF (mantém hash aprovado, requer bytes originais), rebaseline LF com autorização (padroniza, altera proveniência), fixar .gitattributes (evita deriva, altera política de checkout). O check verde do #43 não demonstra execução do gate histórico.

**FATO:** [Issue #41](https://github.com/Saitar0/trilhacodeprod/issues/41), aberta e sem comentários, relata `docker run --pull never mongo:7` sem imagem pré-carregada. **INFERÊNCIA:** provisionar imagem no runner descartável sem relaxar --pull never é alternativa de avaliação humana.

## 8. Execução de testes
**NÃO EXECUTADO:** por proibição expressa de clone, Docker e execução de código do repositório; não há Mongo descartável comprovado. Alegação de 47 testes: **NÃO SEI**.

## 9. Achados priorizados
1. **FATO/Alto:** CI mais recente da main falhou em Docker/G2 e E2E: [run](https://github.com/Saitar0/trilhacodeprod/actions/runs/41074693439).
2. **INFERÊNCIA/Alto:** CI verde do #43 é especializado e não prova homologação completa: [workflow](https://github.com/Saitar0/trilhacodeprod/blob/2383364a35e85c15a79904ee0af7f71d626ac646/.github/workflows/beta61-validation.yml).
3. **FATO/Médio:** decisão de proveniência curricular pendente: [Issue #42](https://github.com/Saitar0/trilhacodeprod/issues/42).

## 10. Não verificado
Reviews/comentários integrais, branch protection, logs completos, busca exaustiva Missão 4, tags/forks, patches de alto risco, 17 writers, SHA-256/EOL curricular, testes, validação HTTP independente de todos os links. Não aprovar merge com base neste relatório.

## 11. Anexo de consultas e decisão de publicação
**FATO:** GET /branches/main; /pulls/{38,39,40,43}; /contents/.github/workflows?ref={main,#43}; raw dos workflows nos SHAs exatos; /commits/{sha}/check-runs?per_page=100 (cinco); /actions/runs/{41121493327,41074693439} e /jobs?per_page=100; /actions/runs?branch=main&per_page=5; /branches?per_page=100&page={1,2,3}; /pulls?state=all&per_page=100&page=1; /releases?per_page=100; /issues/{41,42}; /git/trees/{main,#43}?recursive=1; compare/main...#43 e #39...#43. Data 2026-10-31; hora exata **NÃO SEI**. GET /branches/main/protection e /tags?per_page=100 sem resultado conclusivo pelo conector.

**Árvore:** Decisão 1 permitida: `ci-deploy.yml` [linhas 3–7](https://github.com/Saitar0/trilhacodeprod/blob/22dca64556338a8fa9aaa89ce627a4f4af72317d/.github/workflows/ci-deploy.yml#L3-L7) não dispara push audit/**. Decisão 2 permitida: PR docs-only para main aciona testes/builds Docker locais no runner, não deploy, SSH ou publicação; jobs Coolify exigem dispatch. Este documento é uma auditoria **parcial**, sem aprovação de merge.
