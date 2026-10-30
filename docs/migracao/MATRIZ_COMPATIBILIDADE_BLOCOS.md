# Matriz de compatibilidade dos blocos migrados

**Estado:** diagnóstico no commit `147dc68b81169f66b0ba3802fa2f26e5130923a3`; nenhuma extensão implementada.

## Legenda

* **A — Compatível diretamente:** tipo/campo e comportamento existem.
* **B — Transformável sem perda:** há destino, requer mapeamento explícito.
* **C — Exige extensão de schema/importador:** falta tipo, campo ou relação validada.
* **D — Exige funcionalidade de plataforma:** dado pode ser guardado, falta comportamento/API/UI.
* **E — Decisão editorial/pedagógica:** fonte, destino ou política indeterminável.

Tipos verificados em `backend/seed.py`; renderers em `frontend/src/components/blocks/BlockRenderer.tsx` e `BlockRendererParts.tsx`.

| Tipo da árvore | Destino atual | Classe | Diagnóstico/regra proposta |
|---|---|---:|---|
| Teoria | `theory_text.body` | B | Markdown suportado; preservar divisão, código e ordem. |
| Microtópico | Um ou mais `theory_text`; não há tipo próprio | B | Bloco ordenado; não achatar nem criar nós sem aprovação. |
| Quiz | `quiz.question/options/correct_index/explanation` | D | Campos armazenados, mas API oculta chave e renderer espera chave no cliente; falta tentativa/correção autoritativa. |
| Gabarito (`answer_key`) | Sem tipo no catálogo | C + D | Arquivo fonte separado ligado por ref; requer validação, privacidade, API e regra de revelação. |
| Prática | `practical_challenge`, `exercise_open`, `exercise_objective` | B | Submissão manual existe; escolher por forma da fonte e preservar códigos/aceites/critérios. |
| Solução | Sem tipo privado | C + D | Feedback de submissão não equivale a solução editorial. Requer proteção/revelação. |
| Feedback | `submissions.grading.feedback` | B | Correção manual existe; feedback fixo precisa de associação e visibilidade. |
| Flashcard | `flashcard.front/back` | A | Tipo e renderer existentes; manter ordem/ID. |
| Checklist | `checklist.items` | A/B | Interativo e guarda progresso; não equivale a aceite formal. |
| Aceite de prática | `practical_challenge.acceptance` | B | Campo existe. Arquivo separado requer ligação inequívoca ao desafio. |
| Aceite de entrega | Sem tipo próprio | C | Propor `acceptance_criteria` ligado à entrega; não substituir por checklist. |
| Rubrica | `exercise_open.rubric/criteria` e score opcional | C + D | Escala, descritores, pesos e limiar não são aplicados; requer schema/UI. |
| Entrega/marco | Nó genérico `topic` pode ser filho | B + C | Hierarquia representável; workflow de projeto requer extensão. Não inferir marcos. |
| Escopo de projeto | Nó/blocos genéricos | B | Texto literal pode ser preservado; sem entidade projeto própria. |
| Escolha de stack | Sem estado da escolha do aluno | C + D | Preservar opções sem seleção; persistência exige API/estado/UI. |
| Referência/citação | `reference`, `external_link`, `supplementary` | B | Preservar URL/citação/rótulo; link local vira ref/rota. |
| Conexão curricular | Relações prerequisite/complement/revisit/related | B | Nó-a-nó mapeável; sem relação de bloco ou ordem de exibição. |
| Compartilhado | Bloco tem único `node_id` | C + D | Requer bloco canônico e placements; não duplicar. Definir escopo de progresso. |
| Objetivo/resumo/conexões | Campos e tipos variados | B | Regra por arquivo comum; não concatenar implicitamente. |
| Wikilink | Sem plugin detectado no renderer | E + D | Preservar; raiz do vault não confirmada. |
| Tipo desconhecido | Fallback `GenericBlock` | E; rejeição proposta | Fallback visual não prova semântica; validador exige regra explícita. |

## Catálogo atual

`backend/seed.py` declara `theory_text`, `summary`, `checklist`, `exercise_objective`, `exercise_open`, `practical_challenge`, `quiz`, `flashcard`, `code_snippet`, `video_embed`, `external_link`, `instructor_note`, `review`, `supplementary` e `reference`. Capability `submission` é concedida somente a exercise_objective, exercise_open e practical_challenge. `GenericBlock` é fallback, não suporte semântico.

## Regras recomendadas

1. Não colocar chave, solução ou rubrica privada em `instructor_note` ou texto genérico.
2. Manter gabarito como arquivo-fonte distinto, ligado à questão.
3. Diferenciar checklist, aceite, rubrica e entrega.
4. Preservar escalas/descritores sem normalização.
5. Tipo desconhecido bloqueia conversão até regra, permissão, renderer e testes.
6. Compartilhado é um conteúdo canônico com colocações referenciais.

## Evidências

`backend/seed.py`; `backend/schemas/content.py`; `backend/schemas/submissions.py`; `backend/import_payload.py`; `backend/services/imports.py`; `backend/services/nodes.py`; `backend/services/submissions.py`; `backend/services/progress.py`; `backend/indexes.py`; `frontend/src/components/blocks/BlockRenderer.tsx`; `frontend/src/components/blocks/BlockRendererParts.tsx`; `docs/migracao/RELATORIO_AUDITORIA_GLOBAL.md`.
