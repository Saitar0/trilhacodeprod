# Contrato de Persistência Editorial — 14H.3B

Este contrato descreve exclusivamente o repositório editorial isolado em `backend/curriculum_contract/editorial_persistence.py`. Ele não é uma API pública nem autorização para importar ou publicar o bundle.

## Identidades

`EditorialIdentity` conserva `entity_kind` e `entity_ref` curricular, sem depender de ObjectId. O tipo `block` inclui tipo e proprietário original; `placement` inclui `block_ref` e `subject_ref`; `project` inclui `unit_ref`. A forma é estrita e recebe hash determinístico.

Um bloco canônico é armazenado uma vez por `block_ref`. Uma colocação tem seu próprio `placement_ref` e revisão, aponta ao bloco e assunto, e conserva ordem, proveniência e `progress_scope`. O estado aceito nesta etapa é estritamente `undecided`; o payload do bloco não é copiado. Projetos têm `project_ref`, unidade proprietária e revisão agregada; as listas `deliveries` e `milestones` permanecem separadas, incluindo seus IDs, ordem, corpo e referências.

## Coleções e documentos

| Coleção | Conteúdo | Mutabilidade |
| --- | --- | --- |
| `curriculum_editorial_heads` | Identidade curricular, identidade-hash, revisão atual e número | CAS somente |
| `curriculum_editorial_revisions` | Tipo, identidade, hash, autoria e data da revisão | Imutável |
| `curriculum_editorial_private_payloads` | Payload integral do bloco/colocação/projeto; projeto inclui as referências pinadas | Imutável |
| `curriculum_editorial_events` | Evento mínimo por operação/revisão | Inserção apenas |
| `curriculum_editorial_operations` | Reserva de idempotência e resultado da operação | Estados controlados |

Cada revisão aponta para payload pela identidade estável e `revision_id`. O payload inclui `content_sha256`; a validação recalcula o hash após ler e reconstruir o modelo tipado. Conteúdo, gabaritos, explicações e demais informações privadas não são incluídos em eventos ou metadados de histórico.

## Hash e identidade de revisão

A serialização usa JSON UTF-8, chaves ordenadas, separadores compactos e arrays na ordem original. Os payloads de origem são persistidos com semântica `exclude_unset`: uma propriedade opcional ausente continua ausente, enquanto `null` explícito continua presente. Na releitura, o modelo Pydantic preserva essa distinção em `model_fields_set`, e a validação do hash reconstrói a mesma forma canônica. O hash do conteúdo cobre a versão do schema, tipo da entidade, referência estável e payload exato; projetos incluem também o conjunto ordenado de referências pinadas. O hash de identidade não inclui ObjectIds nem timestamps. O ID da revisão deriva do identificador da operação, tornando o replay do mesmo comando determinístico.

Campos temporais e autoria são metadados de auditoria, fora do hash do conteúdo. Revisões anteriores nunca são atualizadas. O único documento cujo ponteiro muda é o head; a mudança é protegida pela transação e pelo par esperado de revisão ID/número.

## Comandos e estados

Cada comando de escrita recebe ator autenticado, chave idempotente, `expected_revision_id` e `expected_revision_no`. Ambos esperados são nulos na criação e ambos preenchidos na revisão.

- `created`: nova revisão confirmada.
- `unchanged`: comando idêntico foi confirmado anteriormente ou payload idêntico já corresponde ao head; nenhum conteúdo duplicado é criado.
- conflito: identidade, CAS, índice único ou chave idempotente divergem.
- `pending`/`unknown`: reserva existe, mas o resultado não foi comprovado; não iniciar uma nova gravação.
- `retryable`/`not_committed`: abort conhecido; a repetição só é segura com a mesma chave e comando.
- `confirmed`: a transação confirmou o resultado e IDs da revisão.
- `not_found`: ausência de reserva não prova que uma escrita interrompida nunca chegou ao servidor; resultado inconclusivo.

A chave é escopada por `actor_ref` via hash criptográfico de namespace. Reutilização por outro conteúdo ou hash resulta em conflito; não há substituição last-write-wins.

## Pinagem de projetos

Ao criar uma revisão agregada de projeto, cada referência a bloco é resolvida exclusivamente por `block_ref`. Se existir head/revisão válida, o snapshot armazena `revision_id`, número, hash e tipo exatos. Se não existir, armazena explicitamente resolução `unresolved`, sem inventar ID ou versão. Um tipo ou alvo incompatível bloqueia a gravação. Revisões futuras do bloco não alteram pinagens históricas.

O projeto permanece interno; esta etapa não contém estado publicado. Opções de stack são preservadas, mas `stack_selected` diferente de nulo e `variants` não vazias são recusados enquanto D11 estiver adiada.

## Transações e índices

`ensure_indexes(principal)` instala/verifica índices apenas após autorização administrativa. Nenhum TTL é criado. Escritas usam transação MongoDB com snapshot, majority write concern e leitura primária para persistir revisão, payload privado, evento, atualização/inserção do head e confirmação da operação de forma atômica.

Antes da transação, uma reserva idempotente de documento único identifica a intenção. Ela pode permanecer pendente após uma interrupção; isso resulta em estado desconhecido, nunca em sucesso presumido. Sem transações, a operação falha com erro explícito e nenhuma escrita parcial é aceita.

## Autorização

O autorizador recebe somente `EditorialPrincipal` e uma capacidade própria. A ausência ou exceção do autorizador nega acesso. Capacidades:

- `curriculum.editorial.read`
- `curriculum.editorial.content.read`
- `curriculum.editorial.private.read`
- `curriculum.editorial.revision.create`
- `curriculum.editorial.history.read`
- `curriculum.editorial.admin`

Leitura de revisão completa de bloco/projeto exige também acesso privado. Não há endpoint, projeção de aluno ou serializer público. O payload completo usa `repr=False`; mensagens de erro não incorporam conteúdo recebido.

## Restrições deliberadas

O repositório não implementa progresso, publicação, submissões, tentativas, notas, correção, seleção de stack, estado de checklist por aluno, retirada/exclusão, importação ou reconciliação. Não altera rotas, Mongo operacional, frontend, contratos versionados ou fontes curriculares.
