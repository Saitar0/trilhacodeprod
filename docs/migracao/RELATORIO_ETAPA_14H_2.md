# Relatório — Etapa 14H.2: projeção offline de projetos curriculares

**Data:** 2026-10-28
**Estado:** concluída no escopo offline e somente de leitura. Aguardando revisão; nenhuma integração operacional foi iniciada.

## A. Resultado técnico

[IMPLEMENTADO] `backend/curriculum_contract/projects.py` reutiliza `ProjectSpec`, `ProjectDelivery`, `ProjectMilestone`, `ProjectVariant`, os blocos tipados e `validate_contract`. A camada produz snapshots internos imutáveis e uma projeção pública conservadora. Não foi criado um modelo curricular paralelo nem alterada a versão `trilhacode.intermediate/1.2`.

[IMPLEMENTADO] O índice permite consultar por `ProjectSpec.ref` estável e por unidade proprietária. A unidade precisa existir e ser `submodule`. Entregas, marcos e variantes permanecem tipos e listas distintas; os passos são ordenados por `(order, ref)` sem mudar a ordem ou os objetos de origem.

[IMPLEMENTADO] Referências existentes a rubricas, checklists e critérios de aceite são resolvidas por ID e por papel tipado. Cada bloco associado é representado uma vez por referência na projeção do projeto. Corpos Markdown, campos opcionais, referências vazias, metadados e proveniência permanecem no snapshot interno.

[IMPLEMENTADO] A projeção pública usa allowlist explícita para identidade do projeto/unidade, título, escopo e texto instrucional de entregas/marcos. Ela omite blocos anexos de avaliação, referências a esses blocos, opções e seleção de stack, variantes, proveniência, `source_metadata` e qualquer estado de aluno. Markdown permanece texto; não é convertido para HTML.

[NÃO IMPLEMENTADO] Persistência MongoDB, coleções/índices, publicação, endpoints, páginas, submissões de projetos, correção, progresso, importação ou conexão com NodeReader/BlockRenderer/quizzes.

## B. Contagens conferidas no bundle

O arquivo `docs/courses/trilhacode/trilha-code-bulk-import.json` foi validado pelo schema do bundle e suas contagens foram recalculadas sem imprimir conteúdo avaliativo.

| Elemento | Total no bundle | Associado explicitamente aos projetos |
| --- | ---: | ---: |
| Projetos | 15 | 15 projetados |
| Entregas formais | 20 | 20 preservadas |
| Marcos formais | 36 | 36 preservados |
| Projetos com entregas formais | 5 | 5 |
| Projetos com marcos formais | 9 | 9 |
| Projetos sem entrega nem marco formal | 1 | 1 |
| Opções de stack | 8, em 2 projetos | 8, sem seleção |
| `stack_selected` não nulo | 0 | 0 |
| `ProjectSpec.variants` não vazio | 0 | 0 |
| Blocos `acceptance_criteria` | 17 | 16 referências de entrega/marco |
| Blocos `checklist` | 89 | 36 referências de passo; 0 referências no nível do projeto |
| Blocos `rubric` | 178 | 13 referências no nível do projeto; 0 referências no nível de passo |

As contagens da coluna de associações são referências validadas, não uma reclassificação de todos os blocos desses tipos. Os blocos restantes não foram atribuídos artificialmente a projetos. Os 16 critérios referenciados são blocos únicos; o bundle contém 17 blocos `acceptance_criteria` no total.

Todos os projetos apontam a um `CurriculumNode.kind == "submodule"`. Os objetos mantêm `stack_selected: null` e `variants: []`. Nenhuma stack, entrega, marco, versão ou estado de publicação foi inferido.

## C. Identidade, referências e proveniência

- `ProjectSpec.ref` identifica o projeto; `unit_ref` conserva a relação com o submódulo proprietário.
- Entregas e marcos conservam seus próprios `ref`, título, corpo, ordem, listas de referências e proveniência. Não são convertidos em blocos genéricos.
- Variantes são preservadas como estão. As oito `stack_options` não viram `ProjectVariant` e nenhuma seleção é criada.
- Referências de projeto para blocos são verificadas por existência e tipo: checklist → `ChecklistBlock`; rubrica → `RubricBlock`; aceite de passo → `AcceptanceCriteriaBlock`; referências de passo a checklist/rubrica → seus tipos correspondentes. Rubricas precisam declarar o projeto ou passo como alvo; critérios precisam apontar para o passo correto; checklist e conteúdo contextual precisam conservar o proprietário esperado.
- `content_refs` continua sendo a relação genérica tipada definida no contrato, sem conversão para outro tipo. O bloco precisa existir e pertencer ao passo que o referencia.
- Listas de referência não podem conter duplicatas. IDs duplicados entre os contratos fornecidos e unidades ausentes/incorretas falham com diagnóstico.
- `validate_contract` valida estrutura, caminhos e formato do SHA-256 da proveniência. Este adaptador não lê os arquivos de origem e, portanto, não recalcula os hashes individuais da fonte; a verificação de bytes depende de `verify_source_hash` com bytes fornecidos. O SHA do bundle, por sua vez, foi conferido nesta etapa.

## D. Testes e qualidade

[TESTADO] A suíte final selecionada passou com **117 testes**:

```text
unit_tests/test_project_projection.py
unit_tests/test_shared_content_projection.py
unit_tests/test_curriculum_contract.py
unit_tests/test_curriculum_bulk_import.py
unit_tests/test_curriculum_import_adapter.py
117 passed in 24.83s
```

Também passaram:

- Ruff lint nos dois arquivos Python desta etapa.
- Ruff format check nos dois arquivos Python desta etapa.
- Mypy focado nos dois arquivos Python, com `--explicit-package-bases` e cache temporário: sem erros.
- Parsing sintático via AST.
- Verificação manual de whitespace e newline dos cinco arquivos da etapa.

Durante a implementação, as primeiras execuções identificaram problemas nas assertions/seleção de fixtures, que foram corrigidos antes da execução final. Python 3.11 disponível neste ambiente não tinha pytest; a execução de testes foi feita com Python 3.13. Não foram executados testes de MongoDB, banco, rede ou publicação.

## E. Decisões e limites

[PENDENTE] Não existe versão operacional de projeto, entrega ou marco no `ProjectSpec`; nenhuma versão foi inventada. A proposta anterior em `CONTRATO_PROJETOS.md` permanece proposta e não foi convertida em modelo ou política aprovada.

[PENDENTE] O bundle não determina tipos de evidência de aluno, armazenamento/retention de submissões, fluxo de correção manual de projeto, visibilidade de rubricas, persistência do estado de checklist, seleção de stack ou semântica de progresso do projeto.

[IMPLEMENTADO, SOMENTE TÉCNICO] A projeção pública omite rubricas, critérios, checklists, anexos, stack e metadados administrativos. Isso é uma fronteira conservadora do adaptador; não decide a futura audiência de cada tipo.

[PENDENTE] A projeção pública trata título/escopo do projeto e títulos/corpos literais de entrega/marco como texto instrucional do currículo. Nenhuma rota serve essa projeção nesta etapa. Uma futura publicação ainda exigirá validação editorial e autorização de audiência.

## F. Compatibilidade observada

- O backend possui submissões e correção manual para blocos operacionais genéricos, mas não uma entidade/submissão ligada a projeto, versão de projeto, entrega ou marco. Consulte `backend/services/submissions.py`, `backend/routes_submissions.py` e `backend/schemas/submissions.py`.
- Progresso legado usa usuário/nó/bloco; não há identidade de colocação de projeto ou estado de entrega. Consulte `backend/services/progress.py` e `backend/schemas/progress.py`.
- Quizzes têm serviço/versionamento próprios. Não foram conectados a projetos.
- O repositório editorial de atividades da 14F não é repositório de projetos e segue fora das rotas operacionais.
- O importador legado não representa `ProjectSpec`/componentes sem perda e o bundle versionado permanece fail-closed para aquele formato. Nenhuma adaptação ao formato legado foi feita.
- O frontend existente lê nós e blocos. `TypedActivityRenderer` cobre seis atividades tipadas, não o ciclo de vida de projetos. Nenhum componente foi ligado a esta projeção.

## G. Arquivos desta etapa

- `backend/curriculum_contract/projects.py`
- `backend/unit_tests/test_project_projection.py`
- `docs/migracao/RELATORIO_ETAPA_14H_2.md`
- `docs/migracao/CONTRATO_PROJECAO_PROJETOS_14H_2.md`
- `docs/migracao/MATRIZ_INTEGRACAO_PROJETOS_14H_2.md`

## H. Integridade e Git

- Branch: `migracao-estrutura`.
- HEAD: `147dc68b81169f66b0ba3802fa2f26e5130923a3`.
- Índice: vazio.
- Bundle antes/depois: SHA-256 `43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2`.
- Nenhum arquivo curricular original foi alterado por esta etapa.
- Nenhuma conexão ou escrita MongoDB, importação, endpoint ou publicação ocorreu.
- A anomalia Git relatada anteriormente não se reproduziu nesta execução: `git status --short`, `git diff --check` e `git diff --cached --quiet` funcionaram no worktree. O índice permaneceu vazio. Antes desta etapa havia 25 arquivos rastreados modificados e 143 não rastreados; ao final, os mesmos 25 rastreados preexistentes e 148 não rastreados (cinco arquivos novos desta etapa), sem arquivos deletados. A única mensagem adicional foi o aviso de conversão LF/CRLF do bundle já modificado antes desta etapa; seu SHA-256 permaneceu o esperado. Nenhum arquivo rastreado foi alterado por esta etapa.
- A checagem manual de whitespace/newline passou nos cinco arquivos novos. Nenhuma operação de staging ou commit foi executada.

## Parecer

**14H.2 está concluída tecnicamente no escopo de projeção offline.** O contrato tipado atual oferece informação suficiente para uma representação auditável e conservadora dos 15 projetos, sem criar semântica operacional.

**14H.3 não está pronta para persistência operacional sem decisões humanas**, especialmente sobre versão imutável, evidências aceitas, histórico/submissões, correção, audiência de avaliação, checklist, stack, permissões e relação com progresso legado. A próxima ação é revisar os contratos e aprovar ou manter pendentes essas decisões. A 14H.3 não foi iniciada.
