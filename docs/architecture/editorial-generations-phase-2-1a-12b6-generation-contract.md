# Fase 2.1A.12B.6 — Contrato proposto de geração e ativação

**Status:** PROPOSED, não implementado/aprovado.
**Dependências obrigatórias:** ADR-001 (revisão coerente) e ADR-005 (fronteira de dados).
**Baseline de leitura:** `e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636`.

## 1. Unidade de publicação

Recomendação provisória: geração imutável da trilha inteira. Leitores atuais compõem árvore, nós, blocos e relações; requisitos e sequência pedagógica podem cruzar módulos. Geração por nó/módulo reduziria custo e conflito, mas exigiria manifests de composição, resolução de referências e regra de cutover simultâneo. Não recomendar composição até mapear dependências e cache.

| Granularidade | Vantagem | Risco/condição |
|---|---|---|
| Aula/nó | Edições pequenas isoladas | Pode quebrar pré-requisitos, sequência, quiz e references entre nós |
| Módulo | Menor snapshot que trilha | Exige head composto e coerência de navegação inter-módulo |
| Trilha inteira | Um head e uma versão pedagógica coerente | Mais storage/build e conflitos amplos; medir limite/latência |
| Composição híbrida | Reuso de subgerações | Mais de um pointer/dependency graph; atomicidade lógica mais complexa |

“Trilha inteira” é proposta para primeiro corte; tamanho real de conteúdo, limite BSON e custo de leitura não foram medidos para a aplicação. Usar chunks limitados referenciados por manifest, não um documento gigante.

## 2. Identidades distintas

| Identificador | Significado | Fonte/controle |
|---|---|---|
| `track_id` | Agregado editorial e escopo de autorização | Identidade estável existente |
| `revision_id`, `revision_seq` | Snapshot de origem comprometido e ordem monotônica | CAS de ADR-001 |
| `generation_id` | Projeção publicável imutável derivada de revisão | Builder; criada uma vez por operação lógica |
| `operation_id` + fingerprint | Comando lógico/replay; fingerprint vincula ator, escopo, base e payload | Servidor; não é ID de geração |
| `schema_version` | Estrutura/capabilities necessárias para interpretar chunks | Compatibilidade de renderer/API |
| `taxonomy_refs[]` / `catalog_revision` | Semântica global fixada, quando relevante | Catálogo/taxonomia versionados |
| `activity_definition_id`/`evaluation_version` | Definição privada usada em tentativa | Evaluator; tentativa guarda referência exata |
| `session_id` | Estado opaco de estudo validado no servidor | Serviço de sessões; liga aluno/trilha/geração |
| `fencing_token` | Época de escritor longo | Controle CAS; não é revisão nem geração |

Não usar `published_version_id` legado como substituto genérico de todos esses conceitos. No snapshot, attempt de quiz persiste `published_version_id`; isso não fixa árvore, progresso e sessão completos.

## 3. Manifest e estados conceituais

Manifest candidate, sujeito a schema review:

- `track_id`, `generation_id`, `source_revision_id`, `source_revision_seq`;
- `schema_version`, referências imutáveis de taxonomia/catálogo;
- algoritmo/versão de canonicalização e digest; não armazenar segredo ou dado pessoal;
- lista ordenada de chunks com IDs, tipo, quantidade/bytes e digest; referência de payload learner-safe e de payload privado, separados;
- contagens e invariantes de domínio (uniqueness, relações, blocos suportados, quiz-definition refs);
- `operation_id`, fingerprint, actor/service identity, timestamps, parent active generation e `restored_from_generation_id` opcional;
- estado candidate/validation e resultado sem dados privados em logs.

| Estado | Semântica proposta | Mutável? |
|---|---|---|
| `PREPARING` | Chunks private candidate sendo escritos | Sim, somente área isolada da operação |
| `VALIDATING` | Conteúdo fechado aguardando verificações | Estado operacional limitado |
| `READY` | Manifest selado; todos refs/digests/semântica validaram | Imutável para sempre |
| `REJECTED` | Candidata inválida/obsoleta | Imutável como decisão; nunca elegível |
| `ACTIVE` | Não persistir como status duplicado | Derivado somente de `editorial_control.active_generation_id` |
| `SUPERSEDED` | Não persistir como authority | Derivado da lineage/head atual; histórico imutável |

Não persistir simultaneamente `generation.status="ACTIVE"` e ponteiro active: dois documentos poderiam divergir. O único fato de seleção é o head no documento de controle. READY não significa publicamente selecionável, apenas válido como candidato.

## 4. Contratos conceituais

### `BuildGeneration(track_id, source_revision_id, expected_revision_seq, operation_id)`

1. Exige revision imutável e dependências versionadas disponíveis; ator é builder privilegiado, distinto do public reader.
2. Lê somente revision e taxonomy refs fixos; nunca lê live collections para “completar” o snapshot.
3. Grava chunks candidate em namespace privado, com IDs determinísticos ou indexados por operation/generation; write retries são idempotentes por digest/ID.
4. Valida ordem, counts, referential integrity, tipos/capabilities, projeção learner-safe e conteúdo privado separado; compute digests canônicos versionados.
5. Reconfere que revision-base ainda pode ser publicada (head editorial ainda igual ou política permite publicar revisão histórica) na ativação; recommendation is require current revision.
6. Seal final marca manifest READY por CAS sobre status e digest de conteúdo. Depois do selo, nenhuma mutação é permitida.
7. Erros: conflict/stale source, unsupported schema, missing dependency, integrity mismatch, permission denied, transient storage. Retentativa igual volta candidate; fingerprint diferente conflita.

### `ActivateGeneration(track_id, generation_id, expected_revision_id, expected_active_generation_id, operation_id, fencing_token?)`

**Precondições:** manifest READY íntegro; `source_revision_id == current_revision_id` (recomendação); todas as dependências e DTO/evaluator versions suportadas; actor authorized; operation/fingerprint válido; nenhum revocation guard; candidate imutável.

**Único ponto de linearização:** uma atualização atômica do documento `editorial_control`, condicionada a `track_id`, revisão e seq esperados, active generation e publication seq esperados, e fence atual quando aplicável. Atualiza `active_generation_id`, `publication_seq+1` e dados mínimos de receipt/operation para identificar seleção. Nenhuma transação multi-doc é necessária para apontar para objetos já escritos e verificados.

**Pós-condição:** se o CAS confirma sucesso, o head aponta para generation READY existente; leitores novos resolvem esse ID. Se falha, head não muda; candidate continua privada/READY ou rejeitada como obsoleta. Publicação concorrente: exatamente uma vence a mesma base; outra recebe conflito e não é silenciosamente rebased.

**Retry após resposta perdida:** localizar operation por unique ID/fingerprint; verificar a seleção na lineage/receipts retidos. Se já selecionada, reproduzir receipt original, inclusive se o head avançou depois. Caso a prova tenha sido eliminada ou seja ambígua, `RECONCILIATION_REQUIRED`; não selecionar de novo. Manter receipts/lineage até horizonte aprovado ADR-004.

Erro conceitual: `GENERATION_NOT_READY`, `SOURCE_REVISION_STALE`, `ACTIVE_HEAD_CONFLICT`, `FENCE_REJECTED`, `OPERATION_KEY_REUSED`, `INTEGRITY_FAILURE`, `REVOCATION_BLOCKED`, `DEPENDENCY_UNAVAILABLE`, `NOT_AUTHORIZED`, `RECONCILIATION_REQUIRED`. API pública mapeia sem expor conteúdo ou detalhes de segurança.

### `ResolvePinnedGeneration(track_id, context)`

- Sessão validada do servidor: resolve a geração gravada na sessão.
- Leitura sem sessão: lê head uma vez e conserva esse ID durante toda a operação lógica (toda resposta/paginação); endpoint multi-request deve obter referência/session token server-authenticated.
- Busca manifest e chunks **somente** por generation ID fixado, valida digest/refs e a allowlist. Não consulta collections legadas para preencher vazio.
- Chunk/manifest ausente, digest incorreto, schema incompatível, head inválido ou acesso negado: fail closed; resposta indisponível/correlation ID, nenhuma resposta parcial.

### `RestoreAsGeneration(source_revision_id or source_generation_id, current_revision_id, expected_active_generation_id, operation_id)`

- Verifica acesso à origem histórica e que seu schema/taxonomia/evaluator ainda é suportado.
- Cria **nova** revision e generation cujo conteúdo deriva da origem; registra `restored_from_*` e lineage, sem alterar o objeto histórico e sem decrementar sequence.
- Exige mesma validação, selagem e CAS de ativação; conflitos com edição/import/publicação são explícitos.
- Conteúdo removido por política de privacidade/revogação pode ser indisponível para restore e exige decisão de produto/privacidade.

## 5. Modelo integrado revision → generation → head

```mermaid
sequenceDiagram
  participant E as Editor/API
  participant C as EditorialControl (1 doc)
  participant R as ImmutableRevision
  participant B as PrivateBuilder
  participant G as GenerationManifest/Chunks
  participant H as PublicReader
  E->>C: ler revision_id/seq esperado
  E->>R: preparar candidata privada a partir de revisão fixada
  E->>R: CAS current_revision_id + seq
  R-->>E: revisão comprometida
  B->>R: ler somente revisão comprometida + taxonomy refs fixos
  B->>G: gravar chunks privados; validar digest/projeções
  B->>G: selar READY imutável
  B->>C: CAS source revision + active_generation esperado
  C-->>B: head atualizado uma vez
  H->>C: resolver active_generation_id uma vez
  H->>G: ler apenas geração fixada e validar
  G-->>H: allowlist learner-safe
```

Sequência de revisão pode ocorrer em dois commits (conteúdo e depois publicação). Uma mudança editorial concorrente entre build e ativação faz o CAS de publicação falhar se a política exige `source_revision_id == current_revision_id`; candidate fica inativa. Isso evita publicar stale snapshot. Se produto desejar publicar revisão histórica intencionalmente, necessita comando/permissão distinto, mostrando divergência e revisão escolhida, nunca relaxamento silencioso.

## 6. Quizzes e um único head

Recomendação: não manter um segundo ponteiro público independente para quizzes. `tracks.published_activity_version_id` existente é ponteiro de atividade, mas não deve competir com o único head da nova generation.

Quiz que muda independentemente pode ser tratado como nova generation da trilha, copiando/referenciando conteúdo pedagógico imutável não alterado e substituindo apenas a definição private do quiz; o manifest composto e um CAS no mesmo head tornam a experiência uma versão indivisível. Isso tem custo de publicação/armazenamento e decisão pedagógica.

Alternativa é identidade composta `(track_generation_id, activity_generation_id)` com dois heads/selection domains. Leitor poderia ver track A+quiz B durante corrida e sessão/progresso precisa da dupla. Só aceitar com prova de compatibilidade e atomicidade lógica; não é recomendação inicial. Produto define se quiz exige release independente e como progresso atual se comporta.

## 7. Leitura, cache e alunos

- Reader lê um head uma vez por operação; uma operação multi-request utiliza session pin validado pelo backend. `generation_id` do cliente não é autorização.
- Uma leitura iniciada antes do CAS pode terminar somente na generation A; iniciada depois lê B. Nenhuma mistura dentro da resposta lógica.
- Tentativa deve persistir `generation_id`, `activity_definition_id` e evaluator/schema version; avaliação sempre usa definition privada desse pin, não head corrente. O snapshot atual já tem pin limitado `published_version_id` por tentativa, evidenciado por `backend/services/activities.py:72-107,128-190`; não se estende a sessão/tree.
- Cache inclui generation/schema/audience/session semantics; invalidar ou negar revogada conforme política humana. Nunca fallback para `nodes`/`content_blocks` mutáveis.

## 8. Falhas e recuperação

| Falha | Estado permitido | Recuperação |
|---|---|---|
| Crash antes de todos chunks | PREPARING incompleto, não referenciado | Reconciliar/retry com mesmo operation ID; não ativa |
| Crash após chunks, antes seal | Candidate não READY | Verificar digests e concluir ou rejeitar; nunca inferir readiness |
| Crash após READY, antes CAS | Geração íntegra não ativa | Reusar candidate se base/fence ainda atuais, caso contrário stale/rebuild |
| CAS rejeitado por revisão/head/fence | Active head intacto | Retornar conflito; preservar draft; sem automatic rebase |
| CAS teve sucesso, resposta perdida | Head aponta para generation completa | Replay por operation ID e lineage/receipt; não criar segunda publicação |
| Chunk perdido/corrompido após ativação | Head inválido detectado | Fail closed; parar novas publicações, mode read-only/503 e reparar por cópia validada/restore autorizado; não usar live data |
| Duas publicações concorrentes | Só um CAS vence | Outro mantém candidate privada e recebe conflito |
| Restore concorrente com import/edit | Comandos CAS na mesma revisão | Uma vence; outra replaneja somente após decisão explícita; não apagar/resetar head |

## 9. Imutabilidade, armazenamento e limites

Chunks têm identidade por `(generation_id, chunk_id)` e digest; manifest fecha conjunto/order. Unique indexes propostos não estão instalados nem validados. Definir tamanho máximo menor que limite BSON com margem, chunking determinístico, armazenamento de mídia externa referenciada por digest e validação de total bytes. Não incluir progresso, PII nem dados de tentativa em chunks.

“Immutable” é invariável lógico aplicado por serviço/role; MongoDB collection não se torna imutável por nome. Restringir updates/deletes por identidade e code path, auditar maintenance, reter backup/restore e testar tentativa de mutation. GC e idade mínima pertencem ao ADR-004 ainda bloqueado; não remover chunks ou lineage por esta proposta.

## 10. Critérios objetivos de aceitação

1. Controle único é única autoridade de revision e public head; não há pointer concorrente para versão de quiz no caminho novo.
2. Writer legado não consegue alterar estado autoritativo depois do cutover.
3. `READY` implica manifest fechado e todos chunks/refs verificados.
4. Active CAS exige source revision corrente, active head esperado e fence atual.
5. Leitor pinado não consulta dados vivos e verifica integridade, schema e audience.
6. Tentativa usa definição privada versionada pelo pin original.
7. Fault injection cobre crash nos 4 pontos e resposta perdida após seleção.
8. Concorrência comprova um único vencedor, retries idempotentes e stale fencing.
9. Cache e frontend propagam sessão sem autoridade de ID pelo cliente.
10. Topologia/write concern e grant reais foram aprovados e testados em DB descartável.

## 11. Referências

- `backend/services/tracks.py:152-227`, `versions.py:142-159,245-256` — caminho vivo atual.
- `backend/services/immutable_publications.py:461-569` — preparação não elegível (`source_consistency=unverified`).
- `backend/services/nodes.py:85-149`; `activities.py:72-107,128-190,347` — leitores e pin limitado.
- `backend/services/activity_publications.py:155-169` — projeção explícita localizada.
- [`protocolo de revisão`](./editorial-generations-phase-2-1a-12b6-revision-protocol.md), [`fronteira público/privado`](./editorial-generations-phase-2-1a-12b6-public-private-boundary.md), [`invariantes`](./editorial-generations-phase-2-1a-12b6-integrated-invariants.md).
- Prova da PoC é separada: run informado `40686021030`; não valida estes adapters, roles, dados ou implantação real.
