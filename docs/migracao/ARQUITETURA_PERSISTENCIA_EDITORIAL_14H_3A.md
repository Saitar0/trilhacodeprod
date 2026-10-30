# Arquitetura de persistência editorial — Etapa 14H.3A

**Status:** proposta técnica. Não implementada. Todas as políticas de produto descritas como pendentes dependem de aprovação humana.

## 1. Escopo e princípios

Este desenho cobre somente armazenamento editorial futuro para conteúdo compartilhado e projetos curriculares. Não cobre importação, publicação operacional, APIs, renderer, progresso, tentativas de quiz, submissões de alunos ou correção.

Princípios:

- `block_ref`, `placement_ref`, `project_ref`, `delivery_ref` e `milestone_ref` permanecem identidades curriculares externas e estáveis. Não são substituídas por `ObjectId`.
- O payload canônico existe uma vez. Uma colocação aponta para o bloco; não replica seu conteúdo.
- Revisões persistidas são imutáveis. Um head mutável aponta para uma revisão corrente mediante compare-and-swap (CAS).
- Conteúdo público e dados privados avaliativos têm fronteira explícita. Serialização pública usa allowlist positiva e nunca serializa modelos Mongo/Pydantic genéricos.
- Uma referência ausente, versão não resolvida ou conflito bloqueia a operação. O adaptador não inventa IDs, versões, destinos ou decisões.
- Exclusões automáticas são proibidas. Retirada é uma nova decisão/revisão auditável, não apagamento físico.
- `progress_scope: undecided` deve ser persistido literalmente se houver ingestão editorial, sem ativar comportamento de progresso.

## 2. Contratos que já existem

### 2.1 Contrato curricular

`backend/curriculum_contract/models.py` contém `CurriculumNode`, `SharedPlacement`, `ProjectSpec`, `ProjectDelivery`, `ProjectMilestone`, `ProjectVariant`, `ContentBlock` e proveniência tipada. A versão intermediária atual é `trilhacode.intermediate/1.2`; o bundle é `trilhacode.import_bundle/1.0`. Esta proposta não altera nenhuma dessas versões.

`backend/curriculum_contract/validation.py::validate_contract` valida identidades, relações, tipos, referências e proveniência do contrato. `shared_content.py` e `projects.py` são adaptadores offline de leitura, não repositórios.

### 2.2 Repositório editorial 14F

`backend/curriculum_contract/activity_persistence.py` já demonstra o padrão de atividades tipadas: `typed_activity_public_versions`, `typed_activity_private_versions`, `typed_activity_version_events` e `typed_activity_heads`; snapshots imutáveis; hash canônico; CAS por versão esperada; transação; replay idempotente; autorização por permissão. Ele cobre seis tipos de atividade, não `SharedPlacement`, `ProjectSpec`, entrega ou marco. Reutilizar o padrão de segurança e operação é apropriado; reutilizar seus modelos/coleções para projetos ou colocações não é.

### 2.3 Sistemas operacionais existentes

- `backend/services/progress.py`: progresso genérico é identificado por usuário, nó e bloco internos; o índice único em `backend/indexes.py` usa `(user_id, node_id, block_id)`. O contrato curricular ainda não fornece o mapeamento completo entre esses IDs e colocações.
- `backend/services/quizzes.py`: `quiz_versions` identifica versões por quiz e hash; `quiz_progress` é único por `(user_id, quiz_id, version_id)`. O limite atual de três tentativas é por quiz/versão, sem `placement_ref`.
- `backend/services/submissions.py`: submissões genéricas usam usuário, nó, bloco e número de tentativa; a correção existente trata blocos genéricos e permissão `submissions.grade`, sem identidade/versionamento de projeto e entrega.
- `backend/routes_quizzes.py` usa `content.publish` para quiz; `backend/routes_import.py` usa `content.write`. Isso não demonstra que essas permissões sejam adequadas para publicação de projetos.
- `backend/indexes.py` contém índices operacionais atuais. Esta proposta não altera esse arquivo nem afirma que os índices recomendados já existem.

### 2.4 Evidência MongoDB

O relatório [14F.2](RELATORIO_ETAPA_14F2.md) registra testes em MongoDB 9.0.2 com autenticação e replica set descartável de um membro. Foram testadas transações, rollback, concorrência, idempotência, índices e RBAC para o repositório de atividades. Isso não valida a arquitetura aqui proposta, a topologia de produção, failover, eleição de primário ou permissões de coleções ainda inexistentes.

## 3. Alternativas de modelagem

### Conteúdo compartilhado

| Alternativa | Vantagem | Risco/limite | Parecer |
| --- | --- | --- | --- |
| Um documento com payload repetido por assunto | Leitura local simples | Duplica os 406 conteúdos, cria divergência entre 1.001 colocações e dificulta atualização/histórico | Rejeitada: viola identidade canônica e a regra de não duplicar payload |
| Bloco canônico e colocações separadas | Mantém uma identidade do conteúdo e uma relação contextual por assunto | Exige resolver duas referências, versionar ambos e decidir progresso | Recomendada tecnicamente; progresso permanece pendente |
| Um agregado por assunto com blocos copiados | Leitura simples por tópico | Converte referências em clones e perde a identidade compartilhada | Rejeitada |

### Projetos

| Alternativa | Vantagem | Risco/limite | Parecer |
| --- | --- | --- | --- |
| Um snapshot imutável do projeto com arrays separados de entregas e marcos | Consistência de uma versão; componentes preservados; atualização atômica | Alterar qualquer componente cria nova revisão do projeto | Recomendada inicialmente |
| Coleção e ciclo de versão próprios para cada entrega/marco | Atualização independente | Mais transações, referências cruzadas e risco de combinar versões incompatíveis; fonte não define ciclo independente | Só se houver decisão/necessidade de produto |
| Rebaixar projeto a nó/blocos genéricos | Reaproveita renderer existente | Perde tipos, alvos, stacks, ownership, versões e critérios | Rejeitada por perda semântica |

## 4. Modelo lógico recomendado

Os nomes abaixo são **propostas**, não coleções existentes. Usar um namespace dedicado (`curriculum_editorial_*`) para evitar colisão com dados operacionais. `_id` é identidade interna MongoDB; a referência curricular permanece campo explícito e único.

### 4.1 Mapa de identidade curricular

**Alternativa a decidir:** campo `curriculum_ref` nas entidades operacionais existentes ou coleção `curriculum_identity_map`.

Campos propostos: `_id` (`ObjectId`), `source_system`, `entity_kind`, `curriculum_ref`, `mongo_entity_id`, `first_manifest_ref`, `last_observed_manifest_ref`, `created_at`, `updated_at`. Não armazenar texto de resposta/gabarito no mapa.

Índice proposto: único `(source_system, entity_kind, curriculum_ref)`; índice inverso `(source_system, entity_kind, mongo_entity_id)` para impedir dois IDs curriculares apontarem para a mesma entidade quando a cardinalidade for 1:1. O modelo atual não foi consultado em banco e não comprova se `nodes` já guarda uma referência externa estável; não resolver por título, slug ou ordem. A existência desse mapa e sua cardinalidade ficam pendentes do schema real e do snapshot autorizado.

### 4.2 Bloco canônico e revisão

Separar identidade/cabeça e snapshots imutáveis:

| Coleção lógica | Campos obrigatórios propostos | Campos opcionais/privados | Índices/restrições propostos |
| --- | --- | --- | --- |
| `curriculum_block_heads` | `_id`, `block_ref`, `block_type`, `current_revision_id`, `revision_no`, `editorial_state`, `updated_at`, `updated_by` | `owner_ref` original (incluindo `null`), fonte/manifests observados | Único `block_ref`; CAS em `current_revision_id` + `revision_no` |
| `curriculum_block_public_revisions` | `_id`/`revision_id`, `block_ref`, `revision_no`, `block_type`, allowlist do payload de apresentação, `content_sha256`, `source_manifest_ref`, `source_provenance`, `created_at`, `created_by`, `schema_version` | referência de owner, título, ordem de autoria e estado da fonte em metadado editorial não servível | Único `(block_ref, revision_no)` e `revision_id`; lookup `(block_ref, created_at desc)` |
| `curriculum_block_private_revisions` | `revision_id`, `block_ref`, `block_type`, `private_payload` (quando existir), `private_payload_sha256`, `created_at`, `created_by`, `schema_version` | gabarito, solução, feedback reservado, descritores/critério privado e proveniência sensível | Único `(block_ref, revision_id)`; nenhuma role pública com `find` |

“Public” no nome significa apenas snapshot candidato sem campos privados; não significa estado publicado nem acesso de aluno. Por padrão as coleções ficam restritas ao processo editorial. A publicação futura exigiria uma coleção/payload de apresentação explicitamente aprovada.

Não assumir que tipos chamados `feedback`, `rubric`, `checklist` ou `acceptance_criteria` são públicos. A projeção 14H.1 omite seus payloads. Gabaritos e soluções ficam em privado. Um tipo desconhecido não tem payload público até ganhar regra explícita e teste.

A allowlist de apresentação offline já existente em 14H.1 é uma referência técnica fail-closed, não uma decisão de produto nem autorização para servir esses dados. Ela permite `quiz` somente com título, enunciado, formato e alternativas (refs/texto); `practice` somente com enunciado, linguagem e código inicial; e `flashcard` somente com a frente. Omite gabarito, explicação, aceitação, verso de flashcard, proveniência e status. `rubric`, `feedback`, `checklist` e `acceptance_criteria` não têm payload público nesta projeção. Tipos sem regra ficam bloqueados. A 14H.2 também possui uma projeção offline com título/escopo e texto de entregas/marcos, mas ela não está ligada a runtime; audiência desses campos precisa continuar sob revisão editorial antes de qualquer endpoint.

### 4.3 Colocações

| Coleção lógica | Campos obrigatórios propostos | Índices/restrições propostos |
| --- | --- | --- |
| `curriculum_placement_heads` | `_id`, `placement_ref`, `block_ref`, `subject_ref`, `order`, `progress_scope` literal, `current_revision_id`, `revision_no`, `editorial_state`, `updated_at`, `updated_by` | Único `placement_ref`; CAS por revisão; unicidade de `(block_ref, subject_ref)` e `(subject_ref, order)` entre cabeças ativas, **somente se a regra de retirada/estado for aprovada** |
| `curriculum_placement_revisions` | `revision_id`, `placement_ref`, `block_ref`, `subject_ref`, `order`, `progress_scope`, `provenance`, `source_manifest_ref`, `content_sha256`, `created_at`, `created_by` | Único `(placement_ref, revision_no)` e `revision_id`; índices de consulta `(subject_ref, order)` e `(block_ref, subject_ref)` |

O payload do bloco não aparece nas revisões de colocação. A validação confirma que `block_ref` resolve para um bloco canônico compartilhado e `subject_ref` para um `topic`. `progress_scope` não é interpretado para criar progresso. O modelo de origem não declara status de colocação; `active`/`withdrawn` seria uma extensão de persistência que exige aprovação. Até então, nenhuma retirada é inferida.

### 4.4 Projeto, entregas, marcos e variantes

| Coleção lógica | Campos obrigatórios propostos | Campos opcionais/privados | Índices/restrições propostos |
| --- | --- | --- | --- |
| `curriculum_project_heads` | `_id`, `project_ref`, `current_revision_id`, `revision_no`, `editorial_state`, `updated_at`, `updated_by` | referência interna da unidade após mapeamento estável | Único `project_ref`; CAS por revisão |
| `curriculum_project_revisions` | `revision_id`, `project_ref`, `revision_no`, `unit_ref`, `title`, `scope`, `has_formal_deliveries`, arrays `deliveries[]` e `milestones[]` separados, `variants[]` como recebido, `stack_options[]`, `stack_selected`, `checklist_refs[]`, `rubric_refs[]`, `source_metadata`, `provenance`, manifest, hash, autor/data/schema | referências exatas de versão dos blocos após resolução explícita; metadados privados de revisão | Único `(project_ref, revision_no)` e `revision_id`; índices `unit_ref`, `project_ref + created_at desc`; validação de unicidade dos refs filhos antes do commit |

Entrega e marco mantêm cada qual `ref`, `title`, `body`, `order`, refs de aceite/checklist/rubrica/conteúdo e proveniência. O `project_ref` é herdado do agregado e pode ser projetado como ownership derivado, sem alterar o schema fonte. Permanecem em arrays/tipos distintos dentro de uma revisão imutável. Não se criam registros de entrega, marco, submissão ou avaliação para um projeto que não os possui. As oito opções de stack permanecem no campo original; `stack_selected: null` e `variants: []` não são convertidos.

Uma revisão de projeto é armazenada como documento editorial completo, não acessível a alunos. Se futuramente houver publicação, um snapshot público derivado deve ser separado e conter apenas campos cuja audiência tenha sido aprovada. Rubricas/checklists/aceites não podem atravessar essa fronteira por serialização genérica.

### 4.5 Eventos e idempotência

| Coleção lógica | Campos propostos | Índices/restrições |
| --- | --- | --- |
| `curriculum_editorial_events` | `_id`, `operation_id`, `entity_kind`, `entity_ref`, `base_revision_id`, `new_revision_id`, `operation_kind`, `actor_ref`, `at`, `source_manifest_ref`, resultado sanitizado | Único `operation_id`; `(entity_kind, entity_ref, at desc)`; evento append-only |
| `curriculum_editorial_operations` (se ledger separado for escolhido) | `operation_id`, ator/escopo, tipo de operação, entidade, hash canônico do pedido, estado terminal, revision id resultante, data | Único `(actor_scope, operation_id)`; sem payload privado; não expor hash ou erro detalhado a público |

Não registrar respostas, soluções, notas de instrutor ou conteúdo privado em eventos, logs ou mensagens de erro. A necessidade de um ledger separado versus chave idempotente diretamente no evento é uma decisão de desenho para 14H.3B; ambos precisam ser atualizados na mesma transação.

### 4.6 Estados editoriais

`activity_persistence.py` aceita no repositório editorial `draft`, `pending_review`, `structurally_validated` e `publishable`, e impede a entrada de conteúdo já `published` nesse store. Esses valores são evidência do domínio de atividades, não automaticamente o workflow de projeto. Para projetos, recomenda-se separar validação estrutural, revisão editorial e publicação futura; a lista de estados e transições de projeto permanece pendente. Nenhum estado `published` é criado pelo bundle ou pela projeção 14H.2.

## 5. Identidade, revisões e hashes

1. O `*_ref` do contrato é chave externa imutável. Não reescrever prefixos nem derivar identidade de posição/ordem.
2. `_id` interno é `ObjectId` gerado uma vez e persistido. Nunca derivar `_id` da ordem de processamento nem tratar o ref curricular como ObjectId.
3. Cada entidade tem `revision_no` monotônico e `revision_id` interno. O head aponta para exatamente uma revisão; a revisão aponta para os refs curriculares.
4. `content_sha256` é calculado sobre JSON semântico canônico, UTF-8, chaves ordenadas e sem campos voláteis (`created_at`, autor, `_id`, estado de transmissão). O hash público e o hash privado são separados, como no padrão 14F. Não expor hashes privados em payloads públicos.
5. Proveniência conserva manifesto, arquivo e SHA-256 da fonte. Hash do bundle não substitui hash por entidade.
6. Referências entre versões em um snapshot imutável devem fixar `revision_id` dos blocos usados; `block_ref` sozinho resolve apenas a identidade e pode mover para outra versão no futuro. O bundle atual não tem IDs de revisão, portanto não os inventar.
7. Mesmo conteúdo + mesma operação idempotente reconcilia para a mesma revisão. Mesmo `operation_id` com hash diferente é conflito. Mesmo ref/versão com conteúdo divergente nunca é sobrescrito.

Alterar um bloco cria nova revisão do bloco; colocações continuam referindo ao `block_ref` e não são clonadas. Novas apresentações explicitamente versionadas podem apontar para o novo `revision_id`; versões antigas continuam pinadas. A retirada de uma colocação seria registrada como nova revisão/head de colocação e evento de retirada, preservando a identidade canônica e todas as revisões anteriores. O estado `withdrawn` e efeito sobre navegação/progresso precisam de aprovação.

## 6. Transações, CAS e recuperação

### 6.1 Nova revisão de bloco ou projeto

1. Validar o modelo e referências fora do banco; calcular hash canônico; autenticar o ator e verificar permissão.
2. Iniciar sessão/transação. Registrar `operation_id` ou reservar idempotência. Ler head dentro da sessão.
3. Confirmar `expected_revision_id` e sequência. Se não bater, abortar com conflito; não fazer merge de conteúdo implícito.
4. Validar que referências e revisões pinadas existem e estão no estado permitido para a operação solicitada.
5. Inserir snapshot imutável público-seguro e, se existir, snapshot privado com o mesmo `revision_id`; inserir evento/ledger sanitizado.
6. Atualizar head com filtro CAS (`current_revision_id == expected_revision_id` e `revision_no == expected_revision_no`). Para criação inicial, exigir ausência do head com índice único.
7. Confirmar a transação. Leituras e escritas devem usar a mesma sessão; transação requer replica set ou mongos.

### 6.2 Nova revisão de colocação

Transação semelhante. Verificar a existência do bloco canônico e `shared=true`, o assunto `topic`, a unicidade de par ativo e ordem, a proveniência e o `progress_scope` exato. Reordenar várias colocações, se tal operação for aprovada, precisa ser uma transação com validação do conjunto para não deixar ordem duplicada.

### 6.3 Commit incerto, retry e falhas

- Falha pré-transação: nenhuma mutação persistida; retorno pode ser repetido com a mesma operação.
- Falha dentro da transação: abortar; confirmar ausência de revisão/evento/head parcial no teste.
- Timeout durante commit: resultado **desconhecido**, não “falhou”. Consultar pelo `operation_id` em leitura autorizada; se ainda não conclusivo, retornar estado indeterminado sem nova chave.
- Commit confirmado e resposta perdida: replay da mesma operação e hash retorna a revisão já gravada.
- Mesma chave com conteúdo diferente: conflito, sem substituir revisão.
- Versão esperada obsoleta: um escritor vence o CAS; os demais recebem conflito ou reconciliam como replay idêntico. Sem retry com novo `operation_id` automático.
- Erro após commit por falha do cliente: não tentar rollback por delete. Uma correção é nova revisão compensatória, preservando o registro original.

O ledger, snapshots, evento e head precisam compartilhar a mesma transação. Não assumir atomicidade entre documentos/coleções independentes nem entre múltiplas entidades do pacote inteiro. Importação em lote não faz parte desta arquitetura.

### 6.4 Recuperação/rollback

O rollback de uma transação pré-commit é abortar a transação e reler o estado persistido. Depois do commit, a correção é uma nova revisão com base esperada atual, não mutação histórica. Não há TTL ou exclusão automática de revisões/eventos. Retenção legal/operacional de dados de autoria é decisão separada.

## 7. Índices propostos

Todos são propostas para uma instância descartável na 14H.3B; nada foi criado nesta etapa.

| Domínio | Índice lógico | Propósito |
| --- | --- | --- |
| Mapa de identidade | único `(source_system, entity_kind, curriculum_ref)` | Impedir dois internos para a mesma referência externa |
| Heads de bloco | único `block_ref` | Uma cabeça por bloco canônico |
| Revisões de bloco | único `(block_ref, revision_no)`; único `revision_id` | Imutabilidade e lookup |
| Revisão privada | único `(block_ref, revision_id)` | Par privado/público da mesma revisão |
| Heads de colocação | único `placement_ref`; únicos ativos `(block_ref, subject_ref)` e `(subject_ref, order)` | Identidade e integridade contextual, condicionado à decisão de ciclo de vida |
| Revisões de colocação | único `(placement_ref, revision_no)`; lookup `(subject_ref, order)` e `(block_ref, subject_ref)` | Histórico e consulta por tópico |
| Heads de projeto | único `project_ref` | Uma cabeça por projeto |
| Revisões de projeto | único `(project_ref, revision_no)`; único `revision_id`; lookup `(unit_ref, project_ref)` | Histórico e listagem por unidade |
| Eventos/operações | único `operation_id`; lookup `(entity_kind, entity_ref, at desc)` | Replay e auditoria |
| Referências pinadas | índices inversos por `block_ref/revision_id` se materializadas | Localizar consumidores antes de atualização/retirada |

Índices únicos não provam integridade sem validação da aplicação. Duplicidade dentro de arrays de entregas/marcos é verificada pelo schema antes da transação; se o produto exigir consulta/edição independente, reavaliar armazenamento separado. Não usar TTL para histórico. Não criar índices operacionais em `backend/indexes.py` sem autorização e migração específica.

## 8. Fronteira de privacidade e permissões

As permissões abaixo são um desenho de menor privilégio, não permissões existentes nem aprovadas.

| Papel/ação | Leitura permitida proposta | Escrita proposta | Limite |
| --- | --- | --- | --- |
| Aluno/anônimo | Nenhuma coleção editorial. Futuramente, somente snapshot publicado seguro | Nenhuma | Não consultar heads, revisões internas ou privadas |
| Leitor editorial | Revisões editoriais aprovadas para seu escopo; privada apenas se necessário e autorizada | Nenhuma | Não receber acesso automático a gabaritos |
| Editor curricular | Bloco/colocação/projeto internos do escopo; leitura de dados privados conforme necessidade aprovada | Rascunho e nova revisão com CAS | `content.write` não é automaticamente suficiente |
| Editor avaliativo | Conteúdo de correção, rubricas e soluções do escopo | Revisões privadas correspondentes, sem publicação | Permissão separada de leitura de respostas |
| Revisor | Versão candidata e metadados de revisão | Evento de aprovação/rejeição, se fluxo for aprovado | Não altera snapshot já criado |
| Publicador | Somente a revisão aprovada e seus componentes pinados | Ato de publicação separado, futuro | `content.publish` atual é usado pelo fluxo de quiz; não prova adequação a projetos |
| Avaliador de projetos | Submissões/evidências e rubrica autorizada para o projeto/versão | Avaliação append-only futura | `submissions.grade` genérico não implica autoridade em projetos |
| Administrador de banco | Provisionamento técnico conforme operação | Índices/roles em ambiente controlado | Não deve ser identidade da aplicação/aluno; ações auditadas |

Segregação recomendada: role pública com `find` somente em coleção de apresentação futura; sem `find` na revisão editorial ou privada. Editor que precisa validar replay pode precisar de leitura privada, como ocorreu no teste 14F.2; isso exige justificativa e role específica, não privilégio público. Gabaritos/soluções não entram em eventos, logs, exceções nem métricas com rótulo/valor do conteúdo.

Testes obrigatórios na 14H.3B: credenciais distintas; `find` e escrita negados ao papel público nas coleções internas/privadas; allowlist de resposta; consulta por ID/version não contorna RBAC; tentativas de mass assignment; erros/logs sanitizados; auditoria de grants; nenhuma credencial administrativa como prova do papel público.

## 9. Progresso e quizzes — sem decisão

O conteúdo canônico e a colocação têm identidades diferentes. As três alternativas abaixo permanecem abertas:

| Modelo | Chave futura conceitual | Consequência para sistemas existentes |
| --- | --- | --- |
| Global por bloco | `(user, block_ref[, revision])` | Conclusão em um assunto pode aparecer em todos os usos do mesmo bloco. Exige mapear registros atuais `(user, node_id, block_id)`; conflitos entre contextos não podem ser mesclados automaticamente. Quiz atual permanece `(user, quiz_id, version_id)` e compartilha limite/histórico globalmente. |
| Por colocação | `(user, placement_ref[, block_revision])` | Conclusões independentes. Progresso legado não contém `placement_ref`; registros sem mapeamento inequívoco ficam sem backfill. Para quiz, o limite atual por quiz/versão não vira automaticamente por colocação; seria necessário ampliar identidade de tentativa e idempotência sem alterar política de três tentativas. |
| Híbrido explícito | Escopo global ou contextual por item conforme `progress_scope` aprovado | Mantém 1.001 campos `undecided` como bloqueio para o uso correspondente. Exige índice, chave e regra explícitos por escopo; colisões entre chaves não podem ser resolvidas implicitamente. |

Dimensões analisadas: identidade do registro, índice único, compatibilidade histórica, tentativas por quiz/versão, mudança de versão, conclusão cruzada, remoção/realocação, reconciliação e rollback. A tabela completa e alternativas estão em [MATRIZ_PROGRESSO_COMPARTILHADO_14H_1.md](MATRIZ_PROGRESSO_COMPARTILHADO_14H_1.md). Não atualizar `progress_scope`, não mesclar progresso e não conectar `quiz_passed` a uma colocação/projeto até decisão explícita.

Falha na consulta de um pré-requisito avaliativo deve continuar fechando acesso no fluxo tipado existente; esta arquitetura não muda os serviços de progresso nem converte nenhuma das 55 relações curriculares.

## 10. Projetos, submissões e avaliação — alternativas pendentes

- **Submissão:** a coleção `submissions` atual é por bloco e não fixa projeto/versão/entrega. Alternativas: mapeamento explícito ao fluxo genérico com novos campos e invariantes; repositório próprio de submissões de projeto por aluno/projeto/versão/componente; ou evidência fora da plataforma. Recomendação técnica: não reutilizar sem versão e identidade de entrega; considerar agregado dedicado se produto aprovar fluxo próprio.
- **Evidência:** possíveis tipos são texto, URL/commit, arquivo ou referência externa. A fonte curricular não define limite de upload, MIME, malware scan, retenção ou privacidade; nenhum tipo é aprovado.
- **Correção manual:** `submissions.grade` tem estados genéricos. Alternativas incluem extensão do fluxo ou avaliação própria com avaliador, versão de rubric e trilha imutável. Não transformar rubrica em nota nem `approved` legado em conclusão de projeto.
- **Rubrica:** o payload permanece interno por padrão. Revelar dimensões/descritores antes da entrega, depois da entrega ou apenas ao avaliador são opções de produto pendentes.
- **Checklist:** estático/informativo não requer estado do aluno; persistente exige item estável, usuário, versão de projeto, histórico e regra de reabertura. Não escrever no progresso genérico.
- **Stack:** preservar `stack_options`; seleção editorial de uma versão publicada e escolha individual de um aluno são modelos diferentes. `stack_selected: null` continua exatamente nulo; `variants` continua vazio.
- **Projeto sem entregas/marcos:** pode ser exibido futuramente como escopo/atividade do projeto, mas não ganhar submissão, marco ou critério inventado.

## 11. Limites e próximos gates

Esta arquitetura não resolve mapping para nodes de Mongo, semântica dos 55 relacionamentos, raiz do vault, audiência dos blocos, publicação, política de progresso ou política de projeto. Um snapshot de produção não foi consultado. O único teste MongoDB anterior refere-se a atividade tipada em replica set de um membro e não comprova failover ou implantação real.

Antes da 14H.3B: aprovar as decisões identificadas, confirmar o modelo de referência externa dos nodes com schema/snapshot autorizado, determinar se revisão agregada de projeto é aceitável, revisar a matriz RBAC e aprovar retenção/tombstone. Depois disso, implementação somente em repositório isolado e Mongo descartável, ainda sem rotas, importador, progresso ou frontend.

