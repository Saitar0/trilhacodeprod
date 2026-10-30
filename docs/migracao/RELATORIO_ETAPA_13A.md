# Etapa 13A — Arquitetura do adaptador da plataforma

**Estado:** investigação concluída; implementação não autorizada nem realizada.  
**Base examinada:** branch migracao-estrutura, commit 147dc68b81169f66b0ba3802fa2f26e5130923a3.  
**Método:** leitura estática de schemas, serviços, rotas, frontend, testes e artefatos. Não houve chamada ao importador, API ou MongoDB.

## 1. Pré-voo

| Verificação | Resultado |
|---|---|
| Raiz | C:/Users/Joao/.codex/worktrees/fase1-migracao/trilhacodeprod |
| Branch / HEAD | migracao-estrutura / 147dc68b81169f66b0ba3802fa2f26e5130923a3 |
| Git | Índice vazio e arquivos rastreados sem diff; status mostrou itens não rastreados |
| Itens não rastreados | 46 arquivos antes destes três relatórios; preservados |
| Contrato intermediário | 13 arquivos: 10 contratos de fase, source_mappings.json, diagnostics.json, integrity_manifest.json |
| SHA-256 do manifesto | c3f5aa792641408eb66fc80cf801206de4e1deef2130a5a5c436c8d9ade58055 |
| Árvore migrada | 2.890 arquivos presentes |
| Fontes originais | 133 arquivos Markdown presentes; nenhum arquivo rastreado alterado |
| JSON legado | SHA-256 atual 43125c5902168def6359e514ad80602a1f7579157e1a0bb16f1f2212ee4c18e7, igual ao manifesto |
| Banco / importador | Não acessados nem executados |

Os 12 artefatos cobertos pelo integrity_manifest.json conferem com seus hashes. O manifesto não lista seu próprio digest. O contrato registra 131 unidades, 572 nós, 3.431 blocos, 15 projetos, 1.001 colocações compartilhadas, 55 relações, 214 pendências editoriais e 5.344 IDs únicos.

## 2. Arquitetura implementada

A aplicação não possui modelos de domínio distintos para fase, módulo, unidade, assunto ou projeto. Usa coleções genéricas MongoDB: tracks, nodes, content_blocks, relations, progress, learning_events, user_track_state e submissions, além de block_types e taxonomies. Schemas Pydantic usam vários dicts/campos genéricos; essa flexibilidade não valida por si só a semântica curricular.

A hierarquia padrão definida em backend/constants.py:6-7 é phase → module → submodule → topic. Mapeamento proposto: curso para um track; fase para node phase; módulo para node module; unidade para node submodule; assunto para node topic; arquivos curriculares como blocos ordenados no assunto ou unidade conforme manifesto. README é índice/metadado. Entregas só viram nós quando formais na fonte.

O mapeamento é estrutural, mas IDs diferem: refs do contrato são identidades externas, enquanto ObjectId identifica documentos Mongo. O importador procura refs em meta.import_ref. NodeIn não tem campo de slug curricular e services/imports.py deriva slug do título; um adaptador deve preservar os slugs aprovados explicitamente.

backend/seed.py:37-68 registra theory_text, summary, checklist, exercise_objective, exercise_open, practical_challenge, quiz, flashcard, code_snippet, video_embed, external_link, instructor_note, review, supplementary e reference. BlockRenderer.tsx:11-29 tem renderers explícitos e GenericBlock como fallback. Fallback visual não comprova compatibilidade semântica.

## 3. Quizzes e respostas

A API de GET /api/nodes/{node_id} filtra answer, correct_index e explanation para aluno em backend/services/nodes.py:22-34,79-90. O QuizBlock em frontend/src/components/blocks/BlockRendererParts.tsx:42-49 lê correct_index, calcula acerto no navegador e envia correct ao progresso. Com a chave filtrada, o índice padrão é -1 e nenhuma opção é marcada correta. O quiz não tem capability submission. ProgressIn aceita data genérico e services/progress.py:29-58 persiste status/dados do cliente; isso não é correção autoritativa.

Proposta: GET público sem chave; POST de tentativa com ref estável, resposta e token idempotente; correção no servidor; chave/explicação em armazenamento de autoria protegido; resultado para o aluno limitado à política aprovada. Registrar tentativa com aluno, questão, contexto, resposta, resultado, número, instante e versão. Nunca publicar gabarito como theory_text ou instructor_note.

| Política de revelação | Benefício | Custo/risco |
|---|---|---|
| Resposta e explicação após cada envio | Feedback imediato | Facilita compartilhar a chave |
| Certo/errado imediato e chave após condição definida | Protege resposta | Exige regra de tentativas/conclusão |
| Revelação por instrutor | Controle maior | Feedback atrasado |
| Correção no navegador | Simplicidade | Não autoritativa e incompatível com API |

**Decisão pendente:** tentativas, resposta/explicação a revelar e efeitos no progresso. Recomendação técnica não aprovada: correção no servidor, inicialmente retornar certo/errado e liberar explicação conforme política de produto.

## 4. Conteúdo compartilhado e progresso

content_blocks pertence a um node_id. relations conecta nós, não um bloco a vários assuntos com ordem contextual. Placement proposto: placement_ref, block_ref canônica, subject_ref, order e proveniência.

| Política | Efeito para aluno | Consequência |
|---|---|---|
| A. Progresso global por bloco | Concluir em um assunto vale nos outros | Altera percentuais/desbloqueios e difere da chave atual por nó |
| B. Progresso por colocação | Cada aparição mantém estado próprio | Preserva contexto; requer placements e mudança no leitor/API |
| C. Híbrida | Estado oficial contextual; agregado informativo | Conteúdo único e contexto; exige novas estruturas/índices |

A/B/C permanece decisão de produto. Recomendação técnica: C, com progresso por colocação como fonte de verdade; agregados não podem desbloquear. Sem backfill automático.

## 5. Projetos, identidade e reimportação

Não há entidade de projeto. practical_challenge aceita uma lista simples; exercise_open tem rubrica textual; GradeIn guarda resultado, feedback, critérios booleanos e score opcional. Não há comportamento completo para escala, descritores, limiares, múltiplos alvos, entregas ou variantes. Checklist é interação, não aceite formal.

O importador encontra nós por meta.import_ref e blocos por chave node_ref/block_ref; conserva ObjectId de nó existente. Não compara hashes. indexes.py não define índices únicos específicos para refs externas. Nós ausentes ficam intocados. A gravação em services/imports.py:137-195 é sequencial, sem transação global. O snapshot em services/versions.py:118-135 inclui track, nodes, blocks e relations, mas não progresso, submissions ou eventos.

Classificação futura por ref: novo; inalterado se hash e registro coincidirem; atualizado se origem mudou sem divergência manual; conflito se houve edição manual; ausente sem mutação; removido só por tombstone revisado. Título e ordem não são identidade. Nunca excluir por ausência.

Projetos requerem preservação tipada de escopo, entregas, marcos formais, aceites, checklists, rubricas, alvos múltiplos, escalas, limiares, decisões, cenários, revisões e opções de stack. Não inventar marcos ou selecionar stack automaticamente.

## 6. Links, gates e parecer

Link relativo vira ref/rota apenas com destino inequívoco. URL externa permanece referência. Os 94 wikilinks e a raiz do vault Obsidian permanecem pendentes; menções a 47.2/47.3 não criam nós; cópias 37.1/37.2 seguem a decisão editorial da Fase 8. Não criar dependência do guia local não versionado. Referência necessária a tarefa/pré-requisito bloqueia a publicação daquele percurso; nota editorial pode permanecer como texto.

Antes de qualquer escrita na plataforma, decidir: política de quiz; progresso compartilhado; privacidade de solução/instructor note; modelo de projeto/rubrica; IDs/índices; status/publicação; conflitos com edição manual; destino de links funcionais; preservação de progresso/submissions.

O endpoint import dry_run chama planejamento que consulta MongoDB; não é validador offline e não foi executado. A hierarquia é mapeável, mas a árvore não deve ser enviada diretamente ao importador atual. Gabaritos, quizzes, shared placements, projetos, proveniência/hash e referências exigem decisões e/ou extensões.

## 7. Evidências consultadas

Backend: backend/constants.py, database.py, schemas/content.py, schemas/taxonomy.py, schemas/progress.py, schemas/submissions.py, seed.py, routes_content.py, routes_import.py, routes_progress.py, routes_submissions.py, import_payload.py, services/imports.py, services/nodes.py, services/progress.py, services/submissions.py, services/versions.py e indexes.py.

Frontend/testes: frontend/src/components/blocks/BlockRenderer.tsx, BlockRendererParts.tsx, frontend/src/components/student/NodeReader.tsx, frontend/src/components/blocks/ExerciseSubmission.tsx, backend/tests/test_import_workflow.py, backend/tests/test_phase2.py e backend/unit_tests/test_import_payload_shape.py.

Contrato/relatórios: backend/curriculum_contract/models.py, converter.py, validation.py, docs/migracao/contrato_intermediario/integrity_manifest.json, RELATORIO_ETAPA_12D.md, RELATORIO_AUDITORIA_GLOBAL.md e PENDENCIAS_GLOBAIS.md.
