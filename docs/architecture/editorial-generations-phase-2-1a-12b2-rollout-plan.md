# Fase 2.1A.12B.2 — rollout, backfill, recuperação e plano de testes

**Plano futuro; nenhuma etapa abaixo está autorizada ou implementada.** A ordem considera os escritores/leitores encontrados no snapshot `e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636`. Cada fase exige pedido/autorização própria antes de modificar a aplicação, banco, flags ou ambiente.

## 1. Sequência recomendada de rollout

Princípios de ordem:

* Não fazer shadow writes para uma store de gerações a partir de cada rota como substituto do writer canônico: retries, duplicação de efeitos e divergência entre stores são difíceis de reconciliar e não constituem autorização para seleção pública.
* Primeiro instrumentar e definir um único domínio de comando/revisão; depois cercar **todos** os escritores. Construções sombra só podem ler revisões já coerentes e não selecionar head.
* A ativação de leitor público vem depois da migração de escritores, backfill e cobertura de todas as leituras/cache relevantes. Se algum escritor puder contornar revisão/fence, não ativar.

| Fase futura | Objetivo e dependências | Áreas previstas / permitido | Proibido nessa fase | Testes/gate de conclusão | Reversão e autorização |
|---|---|---|---|---|---|
| **2.1A.12B.3 — decisões e ADR** | Aprovar semântica de revisão, conflitos, sessão do aluno, taxonomias, retention e storage; depende desta auditoria | `docs/architecture/`, contratos, threat model | Código, schemas persistidos, flags, banco | ADR assinados pelos responsáveis de produto, backend, segurança e operações; mapa de payload/API | Sem runtime para reverter; autorização documental separada |
| **2.1A.12B.4 — telemetria e linha de base** | Medir comandos e leitura sem mudar comportamento; mapear volume/latência/tamanho/falhas e leitores não descobertos | Instrumentação local em serviços/rotas; logs/metrics sem conteúdo | Writes sombra de estado, novos leitores ativos, migração de dados | Testes de privacidade de logs; métricas por track opaca/resultado, p95 e cobertura; relatório de tráfego e writers | Remover instrumentação/flag; autorização de código/observabilidade |
| **2.1A.12B.5 — modelo de revisão e storage** | Definir schemas versionados, control doc, indexes, roles, limites BSON/retention e recuperação; depende do ADR | Modelos/serviços isolados, migração aditiva planejada, ambiente Mongo descartável | Apontar APIs reais; backfill real; ativar seleção | Testes standalone com índice/grants, falhas em cada etapa, duplicate-key, hashes e limites; ensaio de upgrade/rollback | Coleções novas podem ser deixadas isoladas; rollback exige não selecionar; autorização banco+segurança |
| **2.1A.12B.6 — writers CRUD estruturais** | Migrar track/node/block/relation CRUD, reorder, duplicate, archive/delete para comandos revisionados; depende de B.5 | `tracks.py`, `nodes.py`, `blocks.py`, `relations.py`, rotas e schemas de comando | Permitir writes diretos paralelos às coleções legadas depois do corte; mudar DTO público | API contract tests + concorrência entre campos/entidades + lost response + falhas parciais; provar um CAS vencedor por revisão | Feature interna desativável somente antes do cutover; depois, parar comandos e manter última revisão; autorização separada |
| **2.1A.12B.7 — taxonomias e maintenance** | Decidir e migrar `taxonomies`, `tags`, `block_types`, seeds, migrations e manage commands | `taxonomy.py`, `seed.py`, `manage.py`, `migrations/` | Seed/maintenance contornar fences ou interpretar revisão de forma diferente | Testes de impacto global, capabilities e compatibilidade; controles por ambiente/role | Reverter uso mantendo os objetos versionados; não apagar metadados já referenciados; autorização separada |
| **2.1A.12B.8 — import e restore como comandos** | Converter import recuperável e restore para criar revisão/candidato; depende de todos os writers e política de histórico | `imports.py`, `versions.py`, rotas import/versions, recovery command | `delete_many + insert_many` em conteúdo público ativo; restore que ignore revision/fence | Failpoints antes/depois de cada etapa, retries/replay, concorrência import vs CRUD vs restore, progress preservation | Rejeitar novas operações e manter última generation; restore legado permanece bloqueado após cutover; autorização separada |
| **2.1A.12B.9 — backfill isolado** | Fazer snapshot inicial por track, sem seleção; depende de writer gate/revision protocol e B.5 | Comando de backfill com dry-run, cursor e checkpoint; role limitada | Trocar ponteiro; apagar legado; processar conteúdo sem elegibilidade validada | Repetição idempotente, contagem, hashes, referência órfã, corrupção e resume após processo morto; nenhum head muda | Descartar somente candidatos comprovadamente não referenciados; autorização para operação de dados é separada |
| **2.1A.12B.10 — builder sombra** | Gerar public generation a partir de revision sealed com publicação inativa | Builder e validadores; armazenamento privado | Side effects públicos, writes de rota legacy, seleção de ponteiro | Hash e determinismo; DTO allowlist; validar todos os tipos de bloco; comparar por IDs/hashes sem logar conteúdo | Remover apenas candidatos órfãos via GC delimitado; manter estado de origem; autorização separada |
| **2.1A.12B.11 — comparação e observabilidade de divergência** | Comparar geração sombra com representação legada, sem responder ao aluno | Job/read-only comparator | Fallback automático ou publicação baseada em comparação parcial | Taxa e classe de diferenças, testes de false positive, dados sensíveis não logados; janela estável aprovada | Desligar comparação sem impacto público; autorização separada |
| **2.1A.12B.12 — leitor interno/admin** | Migrar preview/versions e UI staff para generation/revision token antes do público | `get_node`, tree, editor, Versions/Publishing, schemas | Contornar projeção/role; misturar live com generation no mesmo payload | API contract, auth e consistência de duas requests; gerações ausentes/corrompidas falham fechado | Voltar a caminho staff legado somente enquanto nenhum pointer público foi ativado e dados não foram removidos; autorização separada |
| **2.1A.12B.13 — leitor público e cache** | Migrar catálogo, tree, node, busca, atividade e navegação a um generation token fixo | `tracks`, `nodes`, `search`, `learning`, `activities`, frontend query keys | Leitura pública fallback para live; rollout sem cobrir endpoint/worker | Testes concorrentes em todas rotas, DTOs, cache cross-generation, fail-closed, frontend/quiz e E2E | Antes da seleção, desligar leitor novo; após seleção, servir última generation válida/read-only, nunca fallback mutável. Aprovação explícita de operação |
| **2.1A.12B.14 — publicação/restore atômicos** | Trocar publicação e restore por prepare→seal→CAS mantendo contratos externos | `tracks.publish_track`, `versions.restore_version`, control service | Mutar filhos públicos antes do CAS; restaurar por delete/reinsert ativo | CAS disputa, resposta perdida/replay, lost fence, candidato obsoleto, geração inválida; verificação de um único head selecionado | Bloquear novas publicações e manter última geração válida; não voltar a ler live; autorização separada e janela acompanhada |
| **2.1A.12B.15 — remoção do legado** | Encerrar writers/leitores diretos somente após prova de ausência de tráfego e referências | Serviços, schemas e jobs conforme inventário atualizado | Remover histórico/dados sem retention e aprovação humana | Instrumentação demonstra zero uso por janela definida; busca estática + teste de contrato; backup/verificação | Manter compatibilidade de leitura pelo período acordado; rollback de código não reabre fonte mutável; autorização separada |

## 2. Backfill conceitual

1. **Elegibilidade:** track existente e validável; excluir/pausar `_import_state` ativo, restore em andamento, referências incompletas, conteúdo acima dos limites ou schema de bloco sem projeção aprovada. Reportar cada exclusão sem mudar dados.
2. **Ponto de origem:** exigir revisão editorial monotônica controlada pelo protocolo ou congelar writers da track durante captura inicial. Não usar count-before/count-after como prova. Antes de existir revisão comum, snapshot é candidato de migração cuja origem não pode ser chamada de coerente sem quiescência operacional.
3. **Snapshot:** preservar IDs existentes de track/node/block/relation; canonicalizar ordenação e referências; incluir status/ordem/hierarquia, schema de bloco, metadados relevantes e referências privadas de atividade. Não incluir progresso, notas, submissions ou tentativas nos chunks editoriais.
4. **Identidade/idempotência:** deterministic package key `(track_id, source_revision_id, schema_version)` mais operation ID; mesma chave e mesmo fingerprint retoma; chave com conteúdo diferente conflita.
5. **Escrita/resume:** gravar chunks com sequência e hash; checkpoint por operação; retomar somente com mesmo owner/fence ou adquirir novo fence; chunks antigos viram órfãos não selecionáveis. Não modificar manifesto selado.
6. **Validação:** recomputar hash dos bytes e conteúdo canônico; verificar contagem, IDs únicos, `track_id` em toda referência, pai/filho, relações sem dangling/ciclo, quiz schema, referências de atividade, allowlist de público, limites de tamanho; conferir round-trip completo.
7. **Comparação:** reler snapshot legado sob a mesma revisão/congelamento, comparar conjuntos de IDs e hashes por entidade; diferenciar normalização prevista de divergência. Nunca despejar conteúdo ou resposta correta nos logs.
8. **Orfãos:** produzir relatório de referências sem pai/bloco, progress orphaned, submissões existentes e IDs já removidos. Não apagar; preservar registros de aluno e histórico, aplicar tombstone conforme decisão de produto.
9. **Critério “migrada”:** manifest `sealed`, todos hashes/refs válidos, relatório sem diferenças não aprovadas, writer gate ativo, revisão de origem comprovada e registro auditável. Backfill não muda `active_generation_id`.
10. **Amostragem e cutover:** completar todas as elegíveis de uma coorte e comparar antes de escolher uma única trilha piloto; seleção exige gate de fase próprio.

## 3. Feature flags propostas

Todas começam `false`, sem alteração nesta auditoria. Flags independentes impedem que um switch único mude toda a superfície.

| Flag proposta | Escopo | Pré-condições / observação | Parada e reversão |
|---|---|---|---|
| `editorial_revision_commands_enabled` | Escritas administrativas por track/coorte | Todos os writer routes/jobs/maintenance passam por command service; métrica `legacy_writer_calls=0` no escopo | Se CAS conflict/erro aumentar ou bypass ocorrer: rejeitar comandos novos e manter revisão antiga; não aceitar legacy writes no mesmo escopo |
| `editorial_generation_shadow_build_enabled` | Construção privada | Revisão imutável e limites aprovados; medir falhas/hash/órfãos sem publicar | Desligar builder; não selecionar candidatos incompletos |
| `editorial_generation_compare_enabled` | Comparação read-only | Snapshot de origem confiável; registrar somente contagens/hash/categorias | Desligar comparador; abrir investigação se divergence acima do limite |
| `editorial_generation_admin_read_enabled` | Preview interno | Auth/DTO e reader fechado testados; sem fallback invisível | Desligar e parar preview; preservar manifest/chunks |
| `editorial_generation_student_read_enabled` | Coorte/piloto de leitura pública | Todos endpoints/cache/atividade cobertos e dados prebackfilled | Se erro/corrupção, servir geração anterior íntegra ou 503; nunca live fallback |
| `editorial_generation_selection_enabled` | Seleção do pointer | Só após reader consistente e writer fence total | Stop publishing; não “desselecionar” para live sem plano de consistência |
| `editorial_generation_restore_enabled` | Restore versionado | Regras de progresso e historical attempts aprovadas | Parar novas restaurações; geração ativa preservada |

Alteração deve ter dono operacional, registro de justificativa, janela, track/cohort allowlist e métrica antes/depois. Rollback deve ser separado em rollback de código (parar serviço/reader) e rollback de conteúdo (selecionar geração anterior por nova operação validada); não apagar/manipular ponteiro sem receipt e trilha de auditoria.

## 4. Recuperação e rollback

| Falha | Comportamento requerido |
|---|---|
| Antes do primeiro chunk / durante construção | Head ativo permanece; operação fica resumível/abandonável conforme fence; conteúdo partial não é selecionável |
| Depois de chunks, antes de manifest | Retry por operation/fingerprint; chunks não referenciados são órfãos; GC posterior e escopado |
| Depois de manifest sealed, antes de seleção | Geração selada segue privada; revalida contra base/revisão ou abandona como não selecionada; não mutar selo |
| Antes de CAS de seleção | Head anterior serve leitura; retry pode tentar somente se base/revisão ainda forem atuais |
| CAS aplicado, resposta perdida | Buscar receipt por operation_id; retornar mesmo resultado sem segunda seleção; nunca repetir efeito distinto |
| Writer perdeu lease/fence | Todas as transições verificam fence; chunks tardios não alteram refs; writer obsoleto não sela nem seleciona |
| Corrupção de chunk/manifest/head | Leitor falha fechado e alerta; interromper novas publicações; não buscar live; preservar evidência |
| Falha de reader novo | Desligar coorte apenas se caminho anterior não expõe mistura; em produção, última geração íntegra ou indisponibilidade explícita |
| Flag desligada depois do cutover | Bloquear novos comandos/seleções; manter último head/reader confiável até fallback seguro aprovado; não reabrir escritores legacy |
| Restore inválido ou obsoleto | Não alterar head; registrar conflito; criar nova candidata somente após rebase explícito |

Rollback de código não é rollback de dados. Depois de ativar geração, voltar ao leitor mutável só é aceitável se for demonstrado que o modelo legado representa exatamente a geração ativa e nenhum writer parcial pode ocorrer; caso contrário, preservar última geração válida e operar em leitura restrita/indisponibilidade temporária.

## 5. Observabilidade mínima antes dos gates

Logs estruturados sem texto editorial: IDs opacos de operação/generation/track (ou pseudonimizados), fase, estado, duração, tamanho, código de erro, tentativa e resultado. Nunca logar conteúdo, gabarito, resposta, tokens, usuário pessoal ou URI.

Métricas: `editorial_revision_started/sealed/conflict`; `generation_build_started/sealed/selected/abandoned`; `cas_conflict`; `fence_rejected`; `operation_replay`; `integrity_failure` por classe; latency p50/p95/p99 de build/select/read; chunk count/bytes; orphan count/age; backfill eligible/failed/diff category; reader generation pin violations; DTO projection rejection; public read availability; cache hit com generation key; legacy writer call count; fallback attempt (deve ficar em zero depois do cutover).

Alertas antes de ativar: qualquer falha de integridade, pointer sem manifest, fence vencido que tenta selecionar, gabarito encontrado em projection tests, divergência shadow acima do limite, escritor legado observado, fallback público, timeout de build/restore, índice ausente/duplicado e cleanup de candidatos sem propriedade verificável. Não alertar com payload sensível.

## 6. Plano de testes e ambiente

| Grupo | Casos mínimos | Ambiente e critério objetivo |
|---|---|---|
| Unitários | Canonicalização, IDs, schema por bloco, fingerprint, state machine, retries, revision increment, allowlist | Sem DB; determinístico; mesma entrada/hash, inválidos falham fechado |
| Integração MongoDB | Índices únicos, standalone, append-only grants, chunks/manifests, failpoints, CAS, fencing, idempotência e corruption | MongoDB 7 descartável em banco identificado; zero transação multidocumento; todas constraints e erros reais comprovados |
| API | Mesmas rotas/status/payloads/auth, version/generation aditivo, draft/admin/public projection | Test client + DB descartável; contratos existentes preservados ou mudança versionada aprovada |
| Concorrentes | Dois edits de documentos diferentes da mesma revision, reorder vs edit, import vs update, publish vs edit, restore vs publish, reader no swap | Conexões independentes e barreiras; uma revisão/head vencedora; leitor resolve uma geração inteira |
| Frontend | tree/node cross-generation, cache key, troca de sessão, quiz antigo, 409/conflict, generation unavailable | Testes component/integration + navegador QA; sem mistura; UX de atualização indisponível explícita |
| Migração | dry-run, elegibilidade, backfill interrompido/retry, diferença, órfãos, limite BSON, retenção e idempotência | DB sintético descartável; snapshot origem congelado/versionado; nenhuma seleção durante backfill |
| Segurança | append-only, reader sem gabarito, campos extras, tentativa de ler draft/private, bloco desconhecido, role mínima | Mongo real com usuários/roles temporários; API contract + inspeção de campos; teste deve falhar se segredo aparecer |
| Rollback | Falha em todos pontos antes/depois da sela/seleção, resposta perdida, flag off, reader corrupto, última geração | Harness de failpoints e DB descartável; ponteiro antigo preservado antes de commit; depois de commit nunca live fallback |

Gates compartilhados: 100% dos writers/paths inventariados passam pelo fence; todos os readers públicos fixam uma geração; nenhum acesso privado na projeção; documentação/alertas/runbook revisados; índices e topologia reais aprovados; sem skips inesperados; teste completo com concorrência repetida; aprovação humana de produto, segurança e operações para piloto.
