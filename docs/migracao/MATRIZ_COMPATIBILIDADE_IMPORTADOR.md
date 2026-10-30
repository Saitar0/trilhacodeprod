# Matriz de compatibilidade — pacote versionado e plataforma atual

**Referência avaliada:** pacote `trilhacode.import_bundle/1.0`, SHA-256 `43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2`.

Esta matriz descreve capacidades encontradas no código local, não funcionalidades futuras. “Compatível” significa que há uma estrutura alvo compatível; não significa que o bundle seja aceito pelo importador atual. `backend/import_payload.py::validate_import_shape` rejeita `schema_version`, e a rota `/api/import/track` chama `backend/services/imports.py`, que é o importador hierárquico legado.

## Escala

- **A — Direto:** estrutura nativa presente, sem transformação semântica indicada.
- **B — Transformação:** destino existente, com conversão explicitada e preservável.
- **C — Extensão de schema/importador:** falta entidade, campo ou relação estrutural.
- **D — Funcionalidade de plataforma:** exige comportamento de API/renderer/progresso que não existe para aquele tipo.
- **E — Decisão:** a fonte ou a política não define semântica/destino suficientemente.
- **F — Não representável com segurança no fluxo atual:** há risco demonstrado de perda ou exposição.

As classes podem se combinar quando, por exemplo, o schema é adequado, mas o importador versionado não existe.

## Hierarquia e identidade

| Entidade/campo do bundle | Destino existente | Classe | Evidência e limite |
|---|---|---|---|
| Track/currículo | `tracks` | A/C | Coleção e serviço de importação existem. Ainda requer snapshot para distinguir criação/alteração e índice de identidade para a referência externa. |
| `phase → module → submodule → topic` | Nós genéricos em `nodes` | A/B | `backend/constants.py` define `DEFAULT_HIERARCHY = [phase,module,submodule,topic]`; `NodeIn` contém `kind`, `parent_id`, título, ordem/estado/metadados. O importador legado grava `meta.import_ref`, mas não existe índice único de referência curricular em `backend/indexes.py`. O destino usa `ObjectId`; ID curricular não é ID Mongo. |
| Metadados de unidade/proveniência | Campos do nó e `meta` | B/C | Há campos genéricos e `meta.import_ref`; não há schema/importador versionado que garanta round-trip dos metadados e da proveniência completos do contrato. |
| Ordem dos nós e blocos | Campo `order` | A/B | Nós/blocos persistem ordem. A comparação e aplicação determinísticas ainda precisam integrar o importador versionado. |

## Tipos de bloco presentes no pacote

| Tipo no bundle | Quantidade | Classe | Compatibilidade observada / tratamento do dry-run |
|---|---:|---|---|
| `theory` | 379 | B | Transformação proposta para `theory_text.body`; fica pendente de snapshot. Markdown e código devem permanecer literais. |
| `summary` | 123 | A/B | Há tipo `summary` no seed da plataforma; pendente de snapshot e integração do importador. |
| `practice` | 327 | B/D | Transformação candidata para `practical_challenge`; o produto tem submissões desse tipo, mas feedback/solução/rubrica continuam sendo entidades separadas e protegidas. Pendente de snapshot. |
| `flashcard` | 45 | A/B | Tipo de bloco e campos `front`/`back` existem; proveniência e referência curricular ainda dependem de importador versionado. Pendente de snapshot. |
| `reference` | 608 | B/E | 597 referências externas têm URL, rótulo e texto coincidente e podem mapear para `external_link`; 11 destinos/textos não são inequívocos e permanecem pendentes. |
| `quiz` | 506 | C/D/F | O pacote tem 506 questões `format=other`, sem opções. 501 exigem gabarito tipado e 5 não têm gabarito. O serviço atual aceita `multiple_choice` com pelo menos duas opções; 501 ficam bloqueadas, cinco aguardam decisão. |
| `answer_key` | 501 | C/D/F | Não deve virar bloco público genérico. O contrato mantém resposta/explicação em tipo privado; falta caminho de importação/publicação privado para chaves em texto livre e suporte de avaliação correspondente. Bloqueado. |
| `objective` | 131 | C | Não há mapeamento lossless comprovado para o conjunto seed de tipos de bloco. Bloqueado. |
| `checklist` | 89 | C/D | Falta identidade/progresso de item e associação contextual funcional. Bloqueado, sem achatar os itens em teoria. |
| `completion_criteria` | 130 | C/D | Critério curricular tipado e associação não têm destino funcional específico. Bloqueado. |
| `acceptance_criteria` | 17 | C | Precisa preservar alvos, identidade e ligação a entrega/marco/prática. Bloqueado. |
| `rubric` | 178 | C/D | Faltam modelo e fluxo de avaliação de dimensões, escalas, limiares e alvos simples/múltiplos. Bloqueado. |
| `solution` | 212 | C/D/F | Conteúdo protegido e vínculo à prática não têm destino/controle de revelação geral no importador. Bloqueado; não público por `theory_text`. |
| `feedback` | 181 | C/D | Precisa preservar alvo, contexto e regra de revelação. Bloqueado. |
| `instructor_note` | 1 | F | O caminho normal de leitura de blocos não fornece segregação geral por audiência instrutor. Importar como bloco comum poderia expor texto; bloqueado. |
| `project_decision` | 1 | C/D/E | Requer representação de decisão contextual; não deve virar decisão obrigatória de produto. Bloqueado. |
| `project_scenario` | 1 | C/D | Requer cenário tipado e relações de projeto. Bloqueado. |
| `project_review` | 1 | C/D | Requer revisão e perguntas/respostas com semântica própria. Bloqueado. |

**Gabaritos:** os 501 `answer_key` são privados. O plano contém referências e estado de compatibilidade, mas nenhum texto de resposta, explicação ou hash do conteúdo protegido. O serviço quiz atual interpreta chave por `correct_option_ref` e precisa de alternativas estruturadas; não pode corrigir a resposta textual existente sem decisão e implementação explícita.

## Compartilhamento, relações e projetos

| Elemento | Contagem | Classe | Situação |
|---|---:|---|---|
| Blocos canônicos compartilhados | 406 | C/D/E | A plataforma não possui entidade/coleção de colocação canônica por assunto. O bundle possui identidade única para cada bloco e 1.001 referências de colocação; não duplicar os blocos. A semântica de progresso `per_context`/`shared_global` exige decisão separada. |
| Relações `prerequisite` enforced | 35 | E/C | Campo `prerequisite_kind` existe em relações de produção, mas o pacote não distingue `content_completed` de `quiz_passed`. Todas permanecem pendentes; não inferir avaliação. |
| Relações complementares | 16 | A/C | Relação genérica existe. Mapeamento de ID externo e snapshot ainda não foram executados. |
| Relações relacionadas | 4 | A/C | Relação genérica existe. Mesmo limite de identidade/snapshot. |
| Projetos | 15 | C/D | Sem entidade/serviço/renderização de projeto alinhada ao contrato intermediário. Bloqueados. |
| Entregas | 20 | C/D | Texto integral existe no contrato; importador não possui entidade própria para entrega/aceite. Bloqueadas. |
| Marcos formais | 36 | C/D | Nove projetos declaram marcos formais; não inferir marcos nos demais. Estrutura de marcos ainda não tem modelo destino. Bloqueada. |
| Rubricas e checklists de projeto | Incluídos nos blocos acima | C/D | Não achatá-los em textos genéricos; preservar associações e escala/limiar até existir modelo funcional. |

## Referências e pendências editoriais

| Conteúdo | Tratamento | Limite |
|---|---|---|
| Link externo com URL/rótulo/texto consistente | `external_link` é candidato | Não importado; depende de snapshot e de integração. |
| Link interno entre nós | Relação por ID externo é candidata | Resolver identidade no futuro sem fabricar destino. |
| Referência editorial ou destino desconhecido | `pending_decision` | Conservar no lado de auditoria; não converter em link funcional. |
| Wikilink Obsidian | Preservado como referência pendente | Raiz do vault não confirmada; não reescrever. |
| Cópias 37.1/37.2 da antiga pasta da Fase 7 | Mantidas como fontes editoriais não mapeadas | Não declarar aposentadoria nem migrá-las em duplicidade. |
| Referências textuais 47.2/47.3 | Permanecem pendência editorial | Não criar unidades ou destinos fictícios. |
| Nota do instrutor | Bloqueada | Não publicar por caminho comum de aluno. |

O bundle registra 214 pendências editoriais; o dry-run preserva suas identidades/tipos e os 23 casos de referências sem resolução como operações pendentes, sem preencher destino.

## Operações e identidade

- O serviço legado procura nós por `track_id` + `meta.import_ref` e escreve a mesma referência em novos nós; blocos usam `meta.import_ref` composto por nó/bloco. A lista de índices inclui índices de ordem, mas não índice único para essas chaves externas.
- O adaptador propõe `trilhacode:{curriculum_ref}` como chave externa determinística, sem igualá-la ao `_id` MongoDB. A resolução para ObjectId e a garantia concorrente de unicidade ficam para implementação futura.
- Sem snapshot, o dry-run classificou 2.063 operações como `pending_database_snapshot`, 3.016 como `blocked` e 265 como `pending_decision`. Não declarou `create`, `update`, `unchanged` ou `conflict`.
- Um snapshot-only ref aparece em relatório; não se propõe remoção de registros ausentes do pacote.
- A sequência de execução presente no relatório é conceitual e marcada `executable: false`.

## Evidências no repositório

- `backend/import_payload.py::validate_import_shape`: recusa pacotes `schema_version` para evitar carga parcial.
- `backend/routes_import.py::import_track` e `backend/services/imports.py`: rota e executor de importação legados; o planejador legado consulta coleções do banco.
- `backend/schemas/content.py`: `NodeIn`, `BlockIn`, `RelationIn`; bloco usa `type: str` e `data: dict`, e a relação tem `prerequisite_kind` opcional.
- `backend/constants.py`: hierarquia padrão de quatro níveis.
- `backend/services/nodes.py`: caminho de leitura de nós/blocos e filtragem de campos avaliativos; não oferece segregação genérica para `instructor_note` ou `answer_key`.
- `backend/seed.py`: catálogo de tipos de bloco e campos configuráveis.
- `backend/services/quizzes.py`: `_question_snapshot` exige multiple choice/opções e uma chave avaliável; `publish_quiz_version` cria snapshots versionados.
- `backend/routes_quizzes.py`: endpoints autenticados existentes de quiz/revisão/publicação.
- `backend/services/relations.py` e `backend/learning.py`: gravação e interpretação de relações, incluindo pré-requisitos tipados.
- `backend/indexes.py`: índices de nó/bloco e de quiz; não define unicidade por `meta.import_ref` de curriculum.
- `backend/curriculum_contract/models.py` e `backend/curriculum_contract/validation.py`: tipos intermediários e validações de referências.

## Bloqueadores prévios a qualquer escrita

1. Suporte seguro a todos os formatos de quiz/fontes de resposta, ou decisão explícita de tratamento dos 501 gabaritos textuais.
2. Modelos, índices e endpoints para colocação compartilhada e progresso por contexto.
3. Modelos/serviços/frontend para projetos e componentes avaliativos.
4. Segregação de acesso para gabaritos, soluções e notas do instrutor.
5. Classificação editorial das 35 relações enforced.
6. Índices únicos e política de migração para IDs curriculares estáveis.
7. Snapshot sanitizado somente de leitura, após autorização específica.
8. Plano de rollback/compensação e teste isolado em topologia Mongo representativa.

