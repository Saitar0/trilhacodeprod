# Matriz de compatibilidade — contrato intermediário e plataforma

**Base:** commit 147dc68b81169f66b0ba3802fa2f26e5130923a3. Diagnóstico somente; nenhum schema de produção alterado.

## Legenda

1 = compatível diretamente; 2 = transformação explícita sem perda; 3 = exige backend; 4 = exige frontend; 5 = decisão editorial/pedagógica/produto; 6 = não representável sem perda semântica. Mais de uma classe pode aplicar.

| Entidade/campo | Evidência | Classe | Diferença e proposta |
|---|---|---:|---|
| Curso/trilha | TrackIn em schemas/content.py:9-23; tracks | 2 | Um track representa a Trilha; sem nível extra. |
| Fase/módulo/unidade/assunto | DEFAULT_HIERARCHY em constants.py:6-7; NodeIn em content.py:43-59 | 2 | Cabe em phase/module/submodule/topic; refs, pais e ordem explícitos. |
| ID externo | services/imports.py:40-60 usa meta.import_ref | 2/3 | Diferente de ObjectId; faltam índice único e diff por hash. |
| Slug | NodeIn sem slug; services/imports.py:165-170 deriva do título | 3 | Preservar slug curricular em campo/transformação explicitamente validado. |
| Ordem | Importador usa posição de arrays e order de blocos | 2 | Determinística, mas não é identidade. |
| Metadata, proveniência e hash | Meta genérico; importador usa allowlist e não copia proveniência integral | 3 | Persistir source_ref, caminho, hash e versão de conversor explicitamente. |
| Teoria e resumo | theory_text/summary no seed; Markdown renderer | 2 | Blocos separados, Markdown e código literais. |
| Microtópico | Sem entidade/tipo próprio | 2/3 | Corpo pode ser preservado; label/associação requer extensão se funcional. |
| Quiz | quiz em seed.py:53-55; renderer presente | 1 para armazenar; 3/4 no fluxo | API oculta campos que renderer usa; correção local não é autoritativa. |
| Gabarito e explicação | _student_block em services/nodes.py:22-34,79-90 | 3/4/6 | Chave privada, correção server-side e política de revelação; nunca theory_text. |
| Tentativa de quiz | progress genérico; quiz sem capability submission | 3/4 | Nova persistência/endpoint, separado do progresso geral. |
| Prática/exercício | exercise_open, practical_challenge, exercise_objective e submissions | 2 | Mapear formato e preservar instruções, código, critério e solução separados. |
| Solução editorial | Não há tipo privado; feedback de submission é por tentativa | 3/4/6 | Tipo e política de visibilidade necessários; instructor_note não é segredo. |
| Feedback de tentativa | GradeIn e submissions.grading.feedback | 2 | Representa correção individual, não solução estática. |
| Flashcard | seed.py:56 e renderer | 1 | Frente/verso, ordem e identidade mapeáveis. |
| Checklist | checklist em seed.py:40 e renderer/progress | 1/2 | Checklist interativo; não é aceite. |
| Aceite de prática | practical_challenge.acceptance, seed.py:49-52 | 2 | Lista cabe; vínculo precisa ser unívoco. |
| Aceite formal de entrega | Sem tipo no catálogo | 3/4/6 | Estrutura tipada ligada à entrega/marco, não checklist genérico. |
| Critério de conclusão | Sem tipo específico | 3/6 | Preservar corpo, ordem e associação; sem aprovação inferida. |
| Rubrica, escala, limiar e alvos | exercise_open rubric e GradeIn, schemas/submissions.py:11-22 | 3/4/6 | Não há validação de escala, descritores, pesos, alvos múltiplos ou threshold. |
| Projeto/escopo | Sem entidade Projeto; nodes/blocks genéricos | 2 estrutural/3/4 | Tipo funcional necessário sem reduzir escopo ou inventar marcos. |
| Entrega/marco | Node topic estrutural possível; sem workflow | 2 estrutural/3/4 | Entrega e marco distintos, só quando a fonte declarar. |
| Decisão/cenário/revisão | Tipos ausentes do catálogo | 3/4/6 | Preservar como tipos próprios; não achatar nem impor escolha. |
| Variante/stack | Sem seleção por aluno | 3/4/5 | Preservar opções e seleção nula até decisão. |
| Relação curricular | RelationIn nó-a-nó em content.py:99-104 | 2 | Relação explícita cabe; não posiciona bloco. |
| Referência externa | reference/external_link e renderer | 2 | URL/citação/rótulo preservados. |
| Link interno relativo | Ref resolvível pelo mapa | 2/5 | Resolver só destino comprovado; destino necessário ausente bloqueia percurso. |
| Wikilink | Vault/plugin não confirmado | 5/6 | Preservar literal e pendência. |
| Compartilhado/placement | content_block tem um node_id; relation não ordena bloco | 3/4/6 | Nova colocação para bloco canônico, assunto, ordem e proveniência. |
| Progresso compartilhado | services/progress.py:29-58; indexes.py | 2/3/5 | Escolher política global/contextual/híbrida antes de migração. |
| Pendência editorial | Sem entidade operacional específica | 3/5 | Reter no contrato e decidir se bloqueia publicação. |
| instructor_note | Tipo e callout no seed.py:62/BlockRenderer.tsx:15 | 1 visual; 3/4/6 privacidade | Não é canal privado comprovado. |

## Fluxos atuais e limites

| Fluxo | Evidência | Limite |
|---|---|---|
| Import | POST /api/import/track, routes_import.py:7-12 | dry_run consulta Mongo via planejamento; não é offline. |
| Validação | import_payload.py e services/imports.py | Valida payload/ref/hierarquia/catálogo, não contrato intermediário. |
| Renderer | BlockRenderer.tsx:11-29 | GenericBlock é fallback visual, não equivalência. |
| Progresso | routes_progress.py e services/progress.py | Status/data vêm do cliente, não prova de correção. |
| Submissões | routes_submissions.py e services/submissions.py | Fluxo de rascunho, envio, correção manual e retry para tipos com capability. |
| Snapshot/restore | services/versions.py:118-135 | Não inclui progress, submissions nem events. |

**Síntese:** flashcards e apresentação simples de teoria/resumo/checklist são os casos mais próximos de suporte direto. Hierarquia, ordem, práticas e links exigem transformação. Quiz autoritativo, answer_key, soluções privadas, shared placements e projetos completos exigem backend/frontend. Não achatar aceite, checklist, rubrica, entrega, marco, solução, feedback, decisão ou cenário num bloco genérico.
