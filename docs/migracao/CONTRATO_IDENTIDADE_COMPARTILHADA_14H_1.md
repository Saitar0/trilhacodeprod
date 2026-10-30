# Contrato de identidade compartilhada — Etapa 14H.1

## Estado do contrato

[IMPLEMENTADO] Esta etapa reutiliza IntermediateContract versão trilhacode.intermediate/1.2, ContentBlock, SharedPlacement, CurriculumNode e validate_contract. Não introduz novos IDs curriculares, campos de versão no pacote, entidades Pydantic de domínio, endpoints ou modelos de persistência.

## Identidades

- **Bloco canônico:** ContentBlock.ref é a identidade curricular estável. O bloco mantém type, payload tipado, owner_ref original, ordem autoral, título, status existente e provenance.
- **Colocação:** SharedPlacement.ref identifica a colocação. block_ref aponta para o bloco canônico; subject_ref aponta para um CurriculumNode existente de tipo topic; order é a ordem contextual; progress_scope e provenance permanecem como na fonte.
- **Proveniência:** proveniência do bloco e da colocação é mantida separadamente. Não se exige que apontem para o mesmo arquivo: a colocação e o conteúdo podem ter origens documentais distintas.
- **Proprietário:** os blocos compartilhados do pacote usam owner_ref: null, conforme a validação existente. A origem original permanece descrita pela proveniência; não é inventado um proprietário.
- **Versões:** o contrato atual fornece schema_version, source_revision, hashes do manifesto e hashes por proveniência. Não foi criado content_version porque ele não existe na fonte. Versionamento imutável de conteúdo continua dependente de uma decisão/implementação futura.

## Projeção interna offline

build_shared_content_index(contract) valida o contrato inteiro com validate_contract e falha quando há diagnósticos de erro. SharedContentIndex.for_subject(subject_ref) rejeita referência inexistente ou nó que não seja topic.

O resultado SharedSubjectProjection é uma fotografia recursivamente imutável:

    schema_version
    source_manifest
    subject
    canonical_blocks[block_ref]   # payload completo uma vez por identidade
    placements[]                   # ref, block_ref, subject_ref, order, scope, provenance

As colocações contêm referências e metadados contextuais; não contêm cópia do payload canônico. Os blocos do assunto são únicos por block_ref. A ordenação é determinística por (order, ref); a validação preexistente rejeita ordens contextuais duplicadas.

serialize_internal_projection é para auditoria/projeção interna. Inclui conteúdo integral e proveniência e não deve ser usado em payload de aluno, endpoint público, log ou snapshot público.

## Projeção de apresentação fail-closed

A saída pública é criada a partir de uma allowlist positiva, sem serializar model_dump() genérico. Inclui somente referências da colocação, ordem contextual, tipo e conteúdo especificamente permitido:

| Tipo compartilhado | Campos projetados | Campos/dados omitidos |
| --- | --- | --- |
| quiz | title, prompt, format, options (ref, text) | answer_key_ref, answer_key_required, gabarito, explicação, proveniência, status |
| practice | prompt, language, starter_code | critérios acceptance, proveniência, status |
| flashcard | front | back, proveniência, status |
| rubric | nenhum payload | rubrica integralmente retida internamente |
| feedback | nenhum payload | feedback integralmente retido internamente |
| checklist | nenhum payload | checklist integralmente retido internamente |
| acceptance_criteria | nenhum payload | critérios integralmente retidos internamente |

content: null significa apenas que este adaptador não tem uma allowlist aprovada para apresentar aquele tipo; não significa publicação, erro curricular ou exclusão. Uma classe/tipo futuro sem regra explícita causa PUBLIC_TYPE_POLICY_UNDEFINED. Campos desconhecidos também são rejeitados pelo modelo de contrato (extra="forbid").

A omissão das categorias protegidas é uma salvaguarda técnica deste adaptador offline, não uma decisão de produto sobre a futura audiência. Nenhum endpoint ou renderer chama essa projeção.

## Integridade e erros

A projeção reutiliza a validação existente para:

- blocos canônicos ausentes ou não compartilhados;
- consumidores ausentes ou que não sejam tópicos;
- IDs duplicados, pares bloco/assunto duplicados e ordem contextual duplicada;
- estrutura e proveniência inválidas, incluindo caminhos e hashes;
- blocos compartilhados sem colocação;
- referências tipadas do contrato.

Os diagnósticos mantêm código e identidade da entidade, sem incluir corpo do bloco. Nenhum conteúdo é escrito, normalizado ou reclassificado. A projeção conserva exatamente os valores progress_scope de entrada.

## Compatibilidade e limites

- O bundle de origem permanece trilhacode.import_bundle/1.0; os contratos de fase permanecem em trilhacode.intermediate/1.2.
- O contrato operacional atual ainda não possui placement_ref no modelo de progresso; esta etapa não reconcilia nem altera progresso.
- Não há política aprovada de progresso compartilhado.
- Não há integração com MongoDB, importador, API, publicação, NodeReader, BlockRenderer, quizzes ou frontend.
- A raiz do vault e as pendências editoriais continuam fora do escopo.
