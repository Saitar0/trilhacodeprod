# Fase 2.1A.12B.6 — Contrato proposto de revisão editorial

**Classificação:** PROPOSED; material para deliberação, não aprovado e não implementado.
**Baseline de código lido:** `e5bf3147a7f9a5ee02e1a011ffcbf1fb7e0cc636`.
**Confiança:** alta quanto aos caminhos descritos no snapshot; nenhuma conclusão sobre qual revisão está implantada.

## 1. Resposta técnica resumida

Recomenda-se uma revisão monotônica por trilha para o agregado pedagógico que os leitores atuais montam em conjunto: trilha, módulos/nós, blocos, relações e definições de atividade. Cada comando grava uma candidata privada e imutável derivada de uma revisão comprometida; uma única atualização condicional em um documento de controle escolhe a nova revisão. O servidor atribui `revision_seq = base_seq + 1`; somente o compare-and-swap (CAS) bem-sucedido torna a revisão corrente. Conflito é explícito e preserva o rascunho do editor.

Essa recomendação **não** torna uma revisão por trilha suficiente para catálogo global. `reorder_tracks`, taxonomias, tags e tipos de bloco têm escopo compartilhado. Sua semântica deve ser congelada/versionada por referência ou controlada por uma revisão de catálogo/taxonomia separada e fixada na geração. Até a classificação de cada dependência, um snapshot que a leia de forma mutável não é coerente.

## 2. Evidência atual e limites

`OBSERVED` abaixo significa observado no código do snapshot, não em produção. Os nomes `ACTIVE`/“ativo” nas linhas do inventário indicam rota/caminho presente no snapshot, não estado operacional do serviço.

| Caminho no snapshot | Comportamento observado | Consequência para revisão | Confiança |
|---|---|---|---|
| `backend/services/tracks.py:51-95` (`create_track`, `update_track`) | Insere ou atualiza documento vivo; `create_track` inicia `version=0`. | Não há CAS comum com documentos filhos nem revisão editorial monotônica demonstrada. | Alta |
| `backend/services/tracks.py:69-73` (`reorder_tracks`) | Atualiza ordens de várias trilhas. | É mutação de catálogo transversal; um controle por trilha não cobre uma ordenação coerente do catálogo. | Alta |
| `backend/services/nodes.py:61-82,152-206,216-233` | CRUD, cascata e duplicação alteram nós vivos; duplicação também reordena. | Escritores indiretos precisam entrar no mesmo comando revisionado. | Alta |
| `backend/services/blocks.py:12-52` | CRUD/reordenação de blocos em documentos vivos. | Um writer pode mudar conteúdo sem alterar contagem; contagem não é revisão. | Alta |
| `backend/services/relations.py:12-50` | Valida relações por leitura e depois insere/altera/remove. | Duas validações concorrentes podem não representar uma revisão única; revisar ciclo e CAS no agregado. | Alta |
| `backend/services/taxonomy.py:12-91` | CRUD global de taxonomias, tags e tipos; apagar tag aplica `$pull` em referências. | Dependência mutável externa ao agregado; classificar/versionar antes de selar. | Alta |
| `backend/services/tracks.py:152-227` (`publish_track`) | Prepara snapshot/atividade, promove nós e blocos em documentos vivos antes de CAS final da trilha. | O CAS final não torna atômicas as alterações anteriores; exposição parcial é possível por intercalação. | Alta |
| `backend/services/imports.py:80-175,526-699` | Lease por slug e verificações de owner em fases/heartbeat; materialização sequencial de trilha, tags, nós, blocos e relações. | Lease é cooperativa e não condiciona cada escrita de conteúdo; não é fencing compartilhado com CRUD/publicação. | Alta |
| `backend/services/versions.py:142-159,245-256,297-322` | Snapshot compara contagens antes/depois; restore apaga e reinsere nós, blocos e relações em lotes; lease em job. | Mudança de conteúdo com contagem igual passa; lease não protege cada mutação destrutiva; restore deve virar nova revisão candidata. | Alta |
| `backend/services/immutable_publications.py:461-569` | Preparação privada existente marca `source_consistency="unverified"` e `activation_eligible=False`. | Scaffold de preparação não é protocolo de revisão/ativação; o próprio código recusa elegibilidade. | Alta |

Não foi demonstrada uma lista exaustiva de scripts externos, seeds operacionais ou processos de manutenção implantados. O inventário do snapshot é uma baseline de leitura, não prova de cobertura em runtime.

## 3. Unidade de concorrência

| Alternativa | Consistência | Concorrência/UX | Integração com leitores atuais | Recomendação |
|---|---|---|---|---|
| A. Por documento | Fraca para árvore, blocos e relações combinados; muitos heads | Menos conflitos locais, porém composições difíceis | Insuficiente para leitura agregada observada | Não usar como autoridade de publicação |
| B. Por módulo | Preserva módulo, mas relações/pré-requisitos e progresso podem cruzar módulos | Menor conflito que trilha | Exige composição e política para quiz/links cruzados | Possível otimização futura, não primeiro contrato |
| C. Por trilha | Uma revisão abrange o agregado pedagógico da leitura | Conflito amplo; editor precisa resolver explicitamente | Mais coerente com `get_track_tree` e navegação por trilha | Preferida para primeira unidade publicada |
| D. Híbrida: revisão por trilha + catálogo/taxonomia versionados | Delimita o agregado e fixa dependências globais | Mais de um identificador; requer resolver conjunto coerente | Abrange ordenação/catalogação sem inflar a trilha | Preferida com C para conteúdo da trilha |

`OPEN_DECISION`: produto pode preferir edição colaborativa por subárvore; nesse caso, o contrato deve definir composição de revisões e resolver referências entre módulos antes de reduzir a unidade. Não se deve dividir unidade só por custo de conflito.

## 4. Entidades conceituais e autoridade

Proposta de um documento pequeno `editorial_control` por `track_id`, única autoridade de concorrência e seleção. Campos conceituais (não schema aprovado):

| Campo | Semântica |
|---|---|
| `track_id` | Chave imutável do agregado. |
| `current_revision_id`, `revision_seq` | Head editorial comprometido e sequência monotônica. |
| `active_generation_id`, `publication_seq` | Único head público; nulo antes do primeiro cutover. |
| `fencing_token` | Época monotônica para operações longas com lease; não é revisão. |
| `control_schema_version` | Interpretação do documento de controle. |
| `updated_at` | Auditoria/observabilidade, não critério de CAS. |

Uma `revision_id` identifica um snapshot editorial imutável. `revision_seq` ordena revisões comprometidas. `generation_id` identifica uma projeção publicável derivada de revisão. `operation_id` identifica uma intenção lógica/replay. `fencing_token` identifica uma época de posse operacional. Eles não são intercambiáveis. Revisão restaurada recebe sequência nova e referência à fonte histórica; a sequência nunca volta atrás.

O controle é um único documento BSON pequeno e de tamanho limitado. Conteúdo grande permanece em manifests/chunks imutáveis privados. Não embutir lista ilimitada de recibos no controle. Limites de tamanho/contagem e write concern precisam ser decididos/testados antes da implementação.

## 5. Contrato conceitual `CommitEditorialRevision`

### Entrada

`track_id`; `expected_revision_id` e `expected_revision_seq`; `operation_id` estável; `operation_fingerprint` calculado pelo servidor sobre comando normalizado, escopo, ator e revisão-base; identidade autenticada/autorizada; tipo de comando; payload validado; para operação longa, `fencing_token` e `lease_id`.

O cliente pode enviar uma revisão-base observada como precondição, mas não escolhe a revisão resultante nem fornece um token de fence autoritativo.

### Pré-condições

1. Ator autorizado para a operação e trilha.
2. `expected_revision_id/seq` coincide com o controle corrente.
3. Todos os dados usados para construir a candidata são da revisão imutável indicada, ou dependências globais têm identidade de versão fixada.
4. Para comando longo, lease ainda pertence ao operation e o fence enviado corresponde ao controle corrente na hora do commit.
5. `operation_id` inexistente ou corresponde à mesma fingerprint previamente registrada.

### Sequência e visibilidade

1. Validar autorização, payload, operação e revisão-base.
2. Escrever candidata, manifest e chunks sob namespace privado derivado de `operation_id`/`revision_id`; nenhum leitor público consulta essa área.
3. Verificar contagens, IDs únicos, relações/referências, schema/taxonomia fixados, limites de chunk e digest canônico.
4. Gravar manifest de candidata com `parent_revision_id`, sequência proposta `base_seq+1`, actor/op/fingerprint e estado de validação. Candidata é imutável após validação; erros tornam-na inelegível, nunca parcialmente visível.
5. Executar update atômico em `editorial_control` filtrando `track_id`, `current_revision_id`, `revision_seq` e, se aplicável, `fencing_token`; definir `current_revision_id` para candidata e `revision_seq=base_seq+1`. Sucesso desse CAS é o único evento que compromete/torna corrente a revisão.
6. Confirmar o resultado. Se resposta foi perdida, localizar a candidata pelo `operation_id` único e verificar se ela é ancestral da revisão corrente; retornar o recibo original se sim. Se o histórico necessário foi retido/compactado ou a evidência for ambígua, retornar `RECONCILIATION_REQUIRED`; não reaplicar automaticamente.

### Resultado e erros

Retorno: `revision_id`, `revision_seq`, `operation_id`, fingerprint, estado `COMMITTED` e referência de auditoria. Erros internos conceituais: `REVISION_CONFLICT` (HTTP 409 quando derivado de API), `FENCE_REJECTED` (409), `IDEMPOTENCY_KEY_REUSED` (409), `VALIDATION_FAILED` (422), `NOT_AUTHORIZED` (403), `NOT_FOUND` (404), `DEPENDENCY_VERSION_UNAVAILABLE` (503), `RECONCILIATION_REQUIRED` (503/409 conforme contrato API), falha de persistência (503). Não retornar detalhes privados em erro público.

### Retry, interrupção e gaps

- Mesmo `operation_id` + mesma fingerprint: replay do resultado original; nunca cria uma segunda revisão.
- Mesmo ID + conteúdo/escopo/base diferente: conflito, sem escrita canônica.
- CAS concorrente perdido: candidata permanece privada/orfã; operação termina `CONFLICTED` ou `ABORTED`; nova tentativa lógica exige nova revisão-base explícita, não rebase silencioso.
- Sequência é derivada de `base_seq+1`, torna-se comprometida somente com CAS. Candidatas perdedoras podem carregar a mesma sequência proposta; não criam gaps na cadeia comprometida.
- Não impor unicidade global de `revision_seq` sobre todas as candidatas privadas: dois concorrentes podem legitimamente preparar `base_seq+1`. A unicidade de sucessor comprometido vem do CAS no controle/lineage; candidatos rejeitados não integram a sequência autoritativa.
- Processo interrompido antes do CAS deixa candidato não referenciado, elegível a reconciliação/GC futuro, nunca head. Depois do CAS, a revisão está comprometida mesmo que gravação de recibo externo ou resposta falhe; lineage/op-ledger precisa permitir replay.
- Operações idempotentes de negócio não dispensam o mesmo `operation_id`/fingerprint: a chave captura a intenção, não apenas igualdade do resultado.

### Critério de coerência do snapshot

Snapshot é coerente somente quando (a) é construído de uma revisão comprometida e imutável, (b) cada dependência semântica global tem `taxonomy/catalog_version` imutável, (c) manifest enumera exatamente os chunks/objetos esperados, (d) os digests e contagens validam, (e) nenhuma referência aponta fora do conjunto autorizado e (f) o CAS confirma que a revisão-base ainda é corrente na seleção exigida. Verificação de revisão antes/depois de consultar documentos vivos só é suficiente depois de comprovar que **todos** os writers incrementam o mesmo fence e não há alteração invisível; hoje essa cobertura não foi comprovada. Comparação de contagens não detecta conteúdo substituído com cardinalidade igual.

## 6. CAS, lease, fencing, idempotência e lock

| Mecanismo | Protege | Não substitui |
|---|---|---|
| CAS de revisão editorial | Um único sucessor da revisão-base para comandos editoriais concorrentes | CAS de publicação; não torna chunks multidocumento atômicos |
| CAS de publicação | Um único head público a partir do `active_generation_id` esperado | Coerência da revisão-fonte; autenticação; validação de chunks |
| Lease | Reduz trabalho duplicado/indica posse temporária de operação longa | Fencing. Pode expirar, e processo pausado pode retomar |
| Fencing token | Rejeita commits de proprietário antigo por comparação monotônica no ponto canônico | Atomicidade de escritas feitas fora do protocolo |
| Idempotency key + fingerprint | Evita duplicar uma intenção lógica e detecta reutilização divergente | Conflito de estado ou autorização |
| Lock administrativo | Coordena ação humana/operacional | CAS, recuperação, imutabilidade ou segurança contra processo stale |

Para operação longa, cada aquisição/takeover que possa substituir proprietário incrementa `fencing_token` no controle por CAS; worker antigo pode terminar escrita apenas em sua área privada. Toda tentativa de selar/commitar compara token atual, operation ID, lease/owner lógico e revisão-base. Não lhe é permitido editar documentos canônicos “vivos”. Lease é disponibilidade; fence validado no CAS é segurança.

## 7. Topologia MongoDB e limites

O desenho proposto exige somente atomicidade de escrita/leitura de um documento no ponto de seleção, mais objetos imutáveis escritos e verificados previamente. Ele evita depender de transação multidocumento para edição, selagem ou publicação. MongoDB standalone oferece atomicidade por documento, mas isso **não** implica atomicidade multi-documento nem demonstra write concern, journaling, replicação, failover ou durabilidade configurados no ambiente futuro. Escritas de chunks/manifest precisam ser confirmadas antes do CAS, com preocupação de persistência acordada e testada.

Se a implementação optar por transação multidocumento, terá de declarar requisito de replica set ou cluster sharded compatível, validar versão/FCV, read/write concerns, retry/commit indeterminado e operação; a PoC standalone não demonstra essa opção. Isso é decisão de infraestrutura separada, não pressuposto deste contrato.

## 8. Invariantes e testes conceituais

| ID | Invariante | Teste futuro mínimo |
|---|---|---|
| REV-1 | Só CAS vencedor compromete `base_seq+1`; nenhuma duplicação da sequência comprometida. | Duas candidatas na mesma base; exatamente um CAS vence; conflito preserva ambas sem ativar perdedora. |
| REV-2 | Revision resulta de base imutável e de dependências versionadas. | Mutar fonte legada/taxonomia após snapshot não muda a revisão selada; writer não instrumentado bloqueia cutover. |
| REV-3 | `operation_id` é único por escopo e fingerprint; replay idêntico retorna resultado original. | Timeout antes/depois do CAS; repetição após sucessor posterior; key reutilizada com payload divergente. |
| REV-4 | Fence antigo jamais comita após takeover. | Pausar writer, tomar lease com fence maior e retomar writer antigo antes de CAS. |
| REV-5 | Sem fallback para documentos mutáveis; candidata incompleta não é alcançável pelo head. | Omitir chunk/referência, validar falha; reader falha fechado sem consultar coleções legadas. |
| REV-6 | Todos os comandos que mudam semântica do agregado passam pelo mesmo controle. | Cobertura por rota/job/script e tentativa de bypass com credencial/processo antigo. |

Propostas não executadas. Requerem testes unitários de contrato, concorrência no MongoDB descartável com a topologia alvo, testes de falha/retry, API e leitor/frontend. A homologação anterior da PoC não cobre esses contratos da aplicação.

## 9. Decisões ainda humanas

1. Aprovar trilha como unidade inicial, com revisão global separada para catálogo/taxonomia, ou escolher granularidade menor com composição explícita.
2. Definir escopo inicial de escritores e política de edição colaborativa/conflito (409 e preservação do draft são recomendações).
3. Definir se processo de bootstrap exige janela de escrita congelada e como revogar writers antigos.
4. Aprovar semântica de idempotência/retention dos receipts e prazo operacional (sem definir prazo arbitrário aqui).
5. Definir write concern/topologia e RPO/RTO sem assumir que o standalone da PoC corresponda à aplicação.

## 10. Referências

- `backend/services/tracks.py:51-95,152-227` — CRUD, ordenação global e publicação atual.
- `backend/services/nodes.py:61-82,85-149,152-233` — CRUD, leitura agregada e duplicação.
- `backend/services/blocks.py:12-52`; `backend/services/relations.py:12-50` — writers de filhos.
- `backend/services/imports.py:80-175,526-699` — lease e aplicação sequencial.
- `backend/services/versions.py:142-159,245-256,297-322` — snapshot por contagens e restore.
- `backend/services/immutable_publications.py:461-569` — candidata atualmente inelegível.
- Revisão B.5: [`ADR-001`](./editorial-generations-phase-2-1a-12b5-adr001-review.md); nesta fase, [`coexistência de writers`](./editorial-generations-phase-2-1a-12b6-writer-coexistence.md); [`invariantes B.3`](./editorial-generations-phase-2-1a-12b3-invariants.md).
