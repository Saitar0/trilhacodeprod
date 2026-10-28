# Fase 2.1A.12B.3 — roadmap proposto após ADRs

**Estado:** plano futuro; nenhuma fase de código/dados está autorizada.
**Baseline de inventário:** e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636; precisa ser refeito após gate ADR-008.

## 1. Regras comuns para todas as fases

- Cada etapa recebe autorização independente e baseline/escopo registrado.
- Nenhuma feature flag começa habilitada; nenhuma flag existe nesta fase documental.
- Não fazer deploy, backfill nem acesso a banco real sem autorização própria.
- Sem transação multidocumento implícita; provar comportamento em MongoDB 7 descartável antes de cada alteração de persistência.
- Não habilitar seleção pública enquanto algum writer legado puder contornar revisão/fence ou reader puder fazer fallback live.
- Toda alteração tem teste, observabilidade, rollback e owner; código e documentação da etapa anterior não são automaticamente aprovados.
- Escrever em diretórios editoriais protegidos continua proibido conforme escopo desta fase.

## 2. Fases propostas

| Fase | Objetivo e dependências | Escopo/áreas previstas | Testes e gate de conclusão | Risco e reversão | Autorização |
|---|---|---|---|---|---|
| 2.1A.12B.4 | Aprovar ADRs e escolher baseline; depende de decisões humanas e SHA/digest implantado | Só ADRs/documentação e reauditoria contra baseline escolhido | Decisões assinadas; schema/API matrix; nenhum código sem baseline provado | Bloqueio se runtime divergir; replanejar sem merge automático | Documental específica |
| 2.1A.12B.5 | Instrumentar writers/readers e lacunas; depende de B.4 | Rotas/services/jobs/manage; logs/metrics sem payload | Testes de privacidade de logs; contagem de writers legacy e endpoints; owner coverage | Remover instrumentation; nenhuma mudança de efeito | Código/observabilidade própria |
| 2.1A.12B.6 | Definir revisão/fence em modelo isolado, sem alterar APIs públicas; depende ADR-001, B.4 | Serviço/modelo isolado, schemas novos apenas após aprovação | Unit + Mongo standalone: revision CAS, idempotência, failpoints, fence | Não selecionar head; manter coleção isolada e abandonável | Código e persistência separados |
| 2.1A.12B.7 | Converter CRUD de trilha/nó/bloco/relação e ordenação; depende B.6 | tracks.py, nodes.py, blocks.py, relations.py e schemas/rotas do baseline | API compatibility; conflict; concorrência em entidades; zero writes diretos | Antes de cutover desabilitar novos comandos; não reconciliar silently | Autorização por grupo writer |
| 2.1A.12B.8 | Migrar duplicação, exclusão/tombstone, taxonomy, tags, block_types, seed/manage | taxonomy.py, seed/manage/migrations e lifecycle | Sem bypass; impactos de global metadata; referential integrity; env guards | Pausar comandos; preservar dados; rollback aditivo | Autorização e decisão de retenção |
| 2.1A.12B.9 | Adaptar import e restore como commands revisionados | imports.py, versions.py, rotas, recovery | import×CRUD, restore×publish, resume/lost response/failpoints | Bloquear operations novas; nunca apagar ativo | Autorização operacional própria |
| 2.1A.12B.10 | Persistência pública/privada, índices e roles; depende ADR-003/005/004 | Collections/indexes, role docs, adapters | Mongo real descartável; grants; BSON/chunk limits; upgrade/rollback | Manter collections novas sem pointer; no global migrations | DB/security approval |
| 2.1A.12B.11 | Backfill em dry-run/isolado; depende B.7-B.10 e origem estável | Comando retomável, checkpoint, report; sem pointer | Idempotency, hashes/refs, eligibility, orphan report; pointer unchanged | Parar job; candidatos só removidos por GC com ownership | Data operation approval separada |
| 2.1A.12B.12 | Shadow builder e comparator read-only; depende backfill e revision gate | Builder/comparator, métricas sem conteúdo | Determinismo, comparison categories, no public effects, divergence thresholds aprovados | Desligar builder/comparator; não alterar legado | Código/DB authorization |
| 2.1A.12B.13 | Migrar leitores internos/admin/preview | versions/preview/editor read APIs e frontend admin | Auth, DTO, same generation across calls, corrupt/missing fail closed | Desligar admin reader antes de public cutover; sem fallback invisível | Autorização de reader/admin |
| 2.1A.12B.14 | Contratos de sessão, progresso e evaluator pin; depende ADR-002/004/005 | activities, submissions, progress, sessions, frontend quiz | A→B, old attempt evaluation, orphan progress, token ownership, idempotency | Pausar novas sessões/tentativas; manter historical evaluator | Produto + código + privacidade |
| 2.1A.12B.15 | Public reader, catálogo/tree/node/search/cache em geração fixada | tracks/nodes/search/learning, React Query hooks e DTOs | API + browser cross-generation; keys include session/gen; no mixed DTO/fallback | Parar novos readers; servir geração verificada ou indisponibilidade | Operação piloto separada |
| 2.1A.12B.16 | Publicação atômica após zero writer bypass; depende ADR-006 e B.7-B.15 | publish path e selector | CAS races, receipt, lost response, stale revision/fence, failpoints | Stop publishing; manter última generation; sem legacy fallback | Cutover authorization explícita |
| 2.1A.12B.17 | Restauração versionada; depende B.9/B.16 e política pedagógica | Restore service, jobs, frontend/admin | Restore cria nova generation; source integrity; attempts/progress; races | Rejeitar restores novas; preservar head | Autorização de restore própria |
| 2.1A.12B.18 | Rollout por coorte, observação, desativar legado após zero uso | Flags/config, dashboards/runbooks, remover caminhos somente aprovados | Window sem bypass/divergence; all readers/writers; rollback drill | Parar comandos e manter generation; código reversal não volta ao live | Aprovação produto/segurança/operação |

## 3. Gates comuns objetivos

1. SHA/digest do runtime e alvo de deploy conhecidos e iguais ao baseline auditado.
2. 100% dos writers com owner, caminho de fence e teste; scanner e métrica não apontam bypass no escopo durante janela aprovada.
3. 100% dos readers públicos/caches possuem generation/session semantics e DTO allowlist.
4. Grants e índices comprovados no MongoDB descartável da topologia autorizada; sem transaction command não suportado.
5. Backfill é idempotente e não altera pointer; divergência não aprovada é zero para coorte candidata.
6. Integridade e concorrência repetidas sem skips inesperados; critérios quantitativos de latência/disponibilidade aprovados por operação.
7. Política de progresso, retenção, privacidade, correção urgente e restore aprovada.
8. Rollback após seleção mantém geração válida/read-only e nunca reativa reader live automaticamente.
9. Runbook, alertas, owners e procedimento de incidentes exercitados.

## 4. Escopo proibido até gates

Não ativar reader ou selector público, não apagar legado, não executar GC/backfill em dados reais, não aplicar migrations, não sincronizar shadow writes por rota, não supor deploy de branch. Toda etapa posterior exige autorização explícita correspondente.
