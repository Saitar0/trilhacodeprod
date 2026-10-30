# Relatório da Etapa 12C.1 — resolução dos bloqueios do dry-run global

**Data:** 2026-10-27  
**Veredito do dry-run:** sem erros bloqueantes de conversão; pronto para revisão/homologação da conversão integral para o contrato intermediário.  
**Versões:** contrato `trilhacode.intermediate/1.2`, conversor `12c.1`.  
**Base:** branch `migracao-estrutura`, HEAD `147dc68b81169f66b0ba3802fa2f26e5130923a3`.

## Escopo e pré-voo

O trabalho corrigiu apenas o contrato intermediário, o conversor, a validação, os testes e a documentação. Nenhuma árvore homologada, fonte original, JSON, importador, frontend ou banco foi alterado. As conversões foram feitas em memória; nenhum artefato de conversão foi persistido.

- Worktree: `C:\Users\Joao\.codex\worktrees\fase1-migracao\trilhacodeprod`; branch e HEAD conferidos.
- Índice vazio e nenhum arquivo rastreado alterado.
- 2.890 arquivos migrados presentes; os SHA-256 de todos coincidem com `COBERTURA_CONVERSAO_12C.csv`.
- 133 fontes Markdown em `Conteudos/`; comparação Git contra HEAD sem alteração. Os 131 arquivos-fonte associados às unidades estão presentes; duas cópias 37.1/37.2 continuam fora da seleção ativa e intactas.
- JSON legado: SHA-256 `43125c5902168def6359e514ad80602a1f7579157e1a0bb16f1f2212ee4c18e7`; comparação Git contra HEAD sem alteração.
- Os artefatos locais não rastreados preexistentes foram preservados.
- Nenhum backup não localizado é declarado como verificado.

## Resultado resumido

Os 19 erros bloqueantes históricos, distribuídos em 12 arquivos, foram resolvidos pelo parsing explícito e pelas associações tipadas abaixo. A nova conversão global encontrou **0 erros**. Os 66 avisos atuais são casos de raiz Obsidian não confirmada. Não houve alteração textual na árvore: 2.890/2.890 hashes permaneceram idênticos ao baseline da 12C.

| Verificação | Resultado |
|---|---:|
| Unidades / nós / blocos / projetos | 131 / 572 / 3.431 / 15 |
| Mapeamentos de arquivo do contrato | 2.889 em 2.889 caminhos |
| Registros nos relatórios de migração / destinos físicos únicos | 4.311 / 2.879 |
| Colocações compartilhadas / relações / pendências editoriais | 1.001 / 55 / 214 |
| Erros / avisos / informações | 0 / 66 / 1.159 |
| IDs de arquivo / IDs de entidade únicos | 2.890 / 5.344 |
| Frontmatters inválidos / arquivos vazios / referências de destino inválidas | 0 / 0 / 0 |
| Hashes da árvore divergentes do baseline / hashes do JSON divergentes | 0 / 0 |

### Contagens por fase

| Fase | Unid. | Arquivos | Mapeamentos | Nós | Blocos | Projetos | Colocações | Relações | Pendências | Erros |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fase 1 | 10 | 221 | 221 | 43 | 263 | 1 | 95 | 21 | 32 | 0 |
| Fase 2 | 7 | 144 | 143 | 27 | 189 | 0 | 95 | 9 | 15 | 0 |
| Fase 3 | 14 | 313 | 313 | 60 | 378 | 2 | 202 | 25 | 48 | 0 |
| Fase 4 | 17 | 395 | 395 | 77 | 508 | 2 | 205 | 0 | 19 | 0 |
| Fase 5 | 20 | 483 | 483 | 88 | 617 | 2 | 113 | 0 | 22 | 0 |
| Fase 6 | 20 | 449 | 449 | 85 | 503 | 2 | 100 | 0 | 23 | 0 |
| Fase 7 | 7 | 156 | 156 | 36 | 181 | 0 | 25 | 0 | 8 | 0 |
| Fase 8 | 8 | 124 | 124 | 25 | 143 | 2 | 15 | 0 | 11 | 0 |
| Fase 9 | 16 | 301 | 301 | 71 | 331 | 2 | 123 | 0 | 19 | 0 |
| Fase 10 | 12 | 304 | 304 | 60 | 318 | 2 | 28 | 0 | 17 | 0 |
| **Total** | **131** | **2.890** | **2.889** | **572** | **3.431** | **15** | **1.001** | **55** | **214** | **0** |

### Blocos por tipo

| Tipo | Quantidade | Tipo | Quantidade |
|---|---:|---|---:|
| answer_key | 501 | acceptance_criteria | 17 |
| checklist | 89 | completion_criteria | 130 |
| feedback | 181 | flashcard | 45 |
| instructor_note | 1 | objective | 131 |
| practice | 327 | project_decision | 1 |
| project_review | 1 | project_scenario | 1 |
| quiz | 506 | reference | 608 |
| rubric | 178 | solution | 212 |
| summary | 123 | theory | 379 |

A conversão agora apresenta 3.431 blocos, 30 a mais que o total histórico da 12C. A diferença corresponde a entidades tipadas que não eram emitidas quando limites ou alvos falhavam: Fase 2 +1; Fase 3 +16; Fase 4 +6; Fase 5 +3; Fase 6 +4; demais fases sem variação. Os arquivos Markdown mantiveram os mesmos hashes. Respostas/gabaritos, nota do instrutor, aceite de prática e rubricas multi-alvo passaram a ter representação explícita.

## Matriz dos 19 bloqueios históricos

A matriz abaixo reproduz as causas-raiz e o rastreamento individual dos 19 diagnósticos históricos, com evidência, correção, risco e teste de aceitação. Todos foram reexecutados sob o conversor 12C.1: nenhum erro bloqueante permaneceu. Os 12 arquivos envolvidos continuam byte a byte iguais aos arquivos auditados na 12C.
## Causas-raiz propostas

| Causa | Diagnósticos | Regra atual | Correção proposta | Risco principal | Teste de aceitação |
|---|---:|---|---|---|---|
| Fronteiras de quiz/revisão e respostas em cascata | 11 | O parser não cobria todos os formatos literais: perguntas numeradas na linha, separadores após `?`/`?**`, e listas de revisão com marcadores `- `. Os oito `ANSWER_QUESTION_NOT_SELECTED` eram cascata de três fronteiras não reconhecidas em 7.3, 7.5 e 16.3. | Reconhecer linha numerada, marcador inline após `?` ou `?**` quando toda a sequência coincidir exatamente com `itens_origem`; para `project_review_questions`, aceitar lista numerada ou bullets somente com IDs R e quantidade/ordem exatas. | Falsos limites em texto técnico (por exemplo `404`) ou captura de lista que não seja revisão. | Reconstruir Q1–Q5 de 7.3, Q1/Q4/Q5 de 7.5 e R1–R5 de 16.3; exigir identidade, ordem e corpo exatos; sequência incompleta permanece bloqueante. |
| Gabarito de prática tem segmentos com o mesmo ID | 1 | O parser exige uma relação 1:1 entre segmentos e IDs; 5.1/P2 declara duas partes `P2` no mesmo arquivo. | Preservar o corpo integral como uma única solução associada a P2 quando todos os rótulos normalizados são idênticos; não criar duas soluções com a mesma identidade. | Colapsar blocos que deveriam ser respostas diferentes. | Confirmar fonte/manifesto literal de 5.1/P2; uma solução, um vínculo P2, bytes do corpo iguais ao arquivo migrado. IDs distintos continuam exigindo separadores explícitos. |
| Respostas em linhas físicas com linha vazia estrutural inicial | 3 | Em 19.1, `itens_origem` declara Q2/Q3 e o corpo preserva uma linha em branco após frontmatter seguida de duas respostas simples, sem rótulos. | Manter o prefixo vazio no primeiro segmento e parear somente se houver exatamente uma linha física não vazia por ID, em ordem; ambiguidades continuam bloqueantes. | Associar respostas por posição quando houver continuação ou separador interno. | Concatenar as respostas Q2/Q3 e reconstruir o corpo todo; linhas vazias internas, continuação ou contagem diferente permanecem bloqueantes. |
| Aceite de prática não é alvo de projeto | 1 | Critérios de aceite só resolvem IDs de entrega/marco. | Representar `practice_ref` explicitamente, validar existência da prática e exigir exatamente um alvo entre prática, entrega ou marco. | Vincular aceite a prática incorreta. | 9.1/C01 aponta somente para P1; ausência ou referência inválida bloqueia. Projetos continuam vinculados a entregas/marcos. |
| Nota do instrutor é tratada como feedback ligado a exercício | 1 | O conversor procura um bloco-alvo declarado e emite erro quando não existe. | Criar tipo intermediário `instructor_note`, de escopo da unidade e audiência `instructor_only`, preservando corpo, título, ordem e proveniência sem alvo fictício. | Exposição inadvertida a estudantes. | O bloco conserva Markdown/hash e não aparece em projeções de conteúdo do aluno; associação explícita inválida segue bloqueada. |
| Lista compacta de alvos de rubrica é lida como um único ID | 2 | `itens_origem: ["P01,P02,P03"]` é tratado como um rótulo indivisível. | Separar somente strings que correspondam integralmente ao padrão explícito de IDs delimitados por vírgula; preservar ordem e rejeitar duplicatas ou alvos ausentes. | Divisão indevida de texto que não seja lista de IDs. | 27.3 e 27.4 resolvem P01, P02, P03 na ordem; string malformada, duplicada ou alvo inexistente continua sendo erro. |

## Rastreamento individual dos 19 diagnósticos

| Nº histórico | Diagnóstico e origem | Evidência literal / causa imediata | Correção e risco específico | Teste de aceitação |
|---:|---|---|---|---|
| 1 | `ANSWER_BOUNDARY_UNSUPPORTED` — F2 5.1, `90_integracao/02_resposta_esperada_pratica_independente.md` | `itens_origem: ["P2", "P2"]`; o corpo preserva `o cálculo explica ...; Os números dependem ...`. O manifesto da Fase 2 declara esses segmentos como partes da mesma P2. | Unificar os rótulos repetidos em uma única solução, sem descartar o corpo nem multiplicar a prática. Risco: esconder uma divisão real; mitigação: aceitar apenas repetição do mesmo ID e conferir separação literal do manifesto. | Uma `SolutionBlock` para P2 com corpo idêntico ao arquivo de origem; segmentos do checklist continuam independentes. |
| 2 | `QUIZ_BOUNDARY_UNSUPPORTED` — F3 7.3, `02_requisicao_async_resposta_erros/02_quiz.md` | Q1 começa `1. `fetch` recebeu uma resposta HTTP 404.`; o `404.` interno é falso marcador. | Ancorar marcadores na linha; fallback inline restrito a `n. **` e sequência esperada. Risco: deixar de reconhecer quiz inline legítimo; testar o caso 19.1. | Q1–Q5 correspondem, na ordem, a `itens_origem`; reconstituir o corpo original. |
| 3 | `ANSWER_QUESTION_NOT_SELECTED` — F3 7.3, gabarito Q1 | A origem contém `**Resposta: B.** Status HTTP de erro...`; a questão Q1 não foi criada por causa do diagnóstico nº 2. | Correção indireta pelo parser do quiz; não alterar nem reatribuir resposta. | `question_ref` aponta para Q1; resposta e explicação literais preservadas. |
| 4 | `ANSWER_QUESTION_NOT_SELECTED` — F3 7.3, gabarito Q2 | `**Resposta: A.** A pausa afeta a continuação...`; falha em cascata do nº 2. | Como no nº 3. Risco: chave vinculada a outro Q; conferir ID exato. | Vínculo Q2 e texto literal preservados. |
| 5 | `ANSWER_QUESTION_NOT_SELECTED` — F3 7.3, gabarito Q3 | `**Resposta: A.** Primeiro confira o status HTTP...`; falha em cascata do nº 2. | Como no nº 3. | Vínculo Q3 e texto literal preservados. |
| 6 | `ANSWER_QUESTION_NOT_SELECTED` — F3 7.3, gabarito Q4 | `**Resposta: A.** A resposta chegou com sucesso HTTP...`; falha em cascata do nº 2. | Como no nº 3. | Vínculo Q4 e texto literal preservados. |
| 7 | `ANSWER_QUESTION_NOT_SELECTED` — F3 7.3, gabarito Q5 | `**Resposta: A.** O servidor autoriza origens...`; falha em cascata do nº 2. | Como no nº 3. | Vínculo Q5 e texto literal preservados. |
| 8 | `QUIZ_BOUNDARY_UNSUPPORTED` — F3 7.5, `02_network_requisicoes/02_quiz.md` | Q4 começa `4. Network mostra status 404 para uma chamada.`; `404.` não é questão. | Mesma regra estrita do nº 2. Risco: marcador falso em texto técnico; teste específico com 404. | Questões Q1/Q4/Q5 e demais itens do arquivo selecionados sem limites internos; texto integral reconstruído. |
| 9 | `ANSWER_QUESTION_NOT_SELECTED` — F3 7.5, gabarito Q1 | `**Resposta: A.** Network registra solicitações...`; cascata do nº 8. | Corrigir apenas o parsing do quiz; resposta não muda. | Gabarito ligado a Q1. |
| 10 | `ANSWER_QUESTION_NOT_SELECTED` — F3 7.5, gabarito Q4 | `**Resposta: A.** 404 é resposta HTTP...`; cascata do nº 8. | Como no nº 9. | Gabarito ligado a Q4. |
| 11 | `ANSWER_QUESTION_NOT_SELECTED` — F3 7.5, gabarito Q5 | `**Resposta: B.** Uma falha sem status pode ter causas diferentes...`; cascata do nº 8. | Como no nº 9. | Gabarito ligado a Q5. |
| 12 | `QUIZ_BOUNDARY_UNSUPPORTED` — F4 16.3, `01_projeto_trilho_b/Q01_revisao_decisoes.md` | A fonte lista cinco perguntas com marcadores `- `, R1–R5, sob `## Revisão das decisões`. | Parser de lista de revisão com contagem e IDs exatos. Risco: captura de checklist; restringir ao tipo de arquivo `project_review_questions`. | Cinco itens, títulos/corpos e ordem originais; nenhuma resposta adicionada. |
| 13 | `PROJECT_ACCEPTANCE_TARGET_MISSING` — F4 9.1, `90_integracao/C01_criterios_aceite.md` | `itens_origem: ["P1"]`; a fonte diz `**Aceite:** cada tabela tem uma chave identificada...`, dentro da prática P1. | Adicionar alvo explícito de prática ao contrato e ao validador. Risco: aceitar alvo errado; exigir uma única prática existente. | C01.owner_ref e practice_ref resolvem à prática P1; projeto sem entrega não é criado. |
| 14 | `QUIZ_ANSWER_KEY_MISSING` — F5 19.1, Q2 | A fonte original tem linha `2. **Qual evidência sugere N+1?** Uma consulta inicial...`; gabarito migrado traz primeira linha como resposta Q2. O bloco de resposta não foi segmentado. | Corrigir fronteira do arquivo com duas linhas-parágrafo alinhadas a Q2/Q3. Risco: associação posicional; exige IDs declarados, mesma contagem e linhas completas. | Gabarito criado para Q2 com resposta exata da primeira linha e explicação vazia, sem inventar campo. |
| 15 | `QUIZ_ANSWER_KEY_MISSING` — F5 19.1, Q3 | A fonte original tem linha `3. **Por que carregar todas as relações antecipadamente pode ser ruim?** Pode aumentar linhas...`; segunda linha do gabarito. | Como no nº 14. | Gabarito ligado a Q3 com texto literal da segunda linha. |
| 16 | `ANSWER_BOUNDARY_UNSUPPORTED` — F5 19.1, `02_consultas_relacoes_custo/03_gabarito_quiz.md` | Duas linhas-parágrafo simples, na ordem: `Uma consulta inicial seguida...` e `Pode aumentar linhas...`; IDs declarados Q2/Q3. | Reconhecer apenas linhas completas e contagem/ordem exatas, com preservação byte a byte. Risco: conteúdo quebrado em linhas; casos ambíguos continuam bloqueados. | Juntar pares Q2/Q3 e respostas sem qualquer alteração textual; reconstrução exata do corpo. |
| 17 | `INSTRUCTOR_NOTE_TARGET_UNRESOLVED` — F5 23.3, `Nota_do_instrutor.md` | `## Nota do instrutor` e princípios “sem convertê-los em checklist ou atividade de marcação”; não declara item de avaliação-alvo. | Tipo `instructor_note` próprio, proprietário unidade 23.3 e audiência exclusiva do instrutor. Risco: exposição; nenhum vínculo/target inferido. | Texto Markdown e proveniência preservados; tipo não serializado como conteúdo do aluno; sem alvo inexistente. |
| 18 | `RUBRIC_TARGET_NOT_FOUND` — F6 27.3, `90_integracao/RUB_rubrica_praticas.md` | Metadado literal `itens_origem: ["P01,P02,P03"]`; texto de origem: `Rubrica (0–4) por atividade`. | Interpretar lista compacta de IDs explícitos e manter os três alvos ordenados. Risco: dividir metadado não padronizado; aceitar apenas gramática exata de IDs. | `target_refs` corresponde às práticas P01, P02 e P03, sem duplicatas, escala 0–4 intacta. |
| 19 | `RUBRIC_TARGET_NOT_FOUND` — F6 27.4, `90_integracao/RUB_rubrica_praticas.md` | Mesmo metadado `P01,P02,P03`; rubrica declara `por atividade`. | Como no nº 18. | Três alvos reais em ordem, escala e Markdown originais preservados. |


### Reconciliação dos códigos históricos

| Código bloqueante histórico | Ocorrências |
|---|---:|
| ANSWER_BOUNDARY_UNSUPPORTED | 2 |
| ANSWER_QUESTION_NOT_SELECTED | 8 |
| INSTRUCTOR_NOTE_TARGET_UNRESOLVED | 1 |
| PROJECT_ACCEPTANCE_TARGET_MISSING | 1 |
| QUIZ_ANSWER_KEY_MISSING | 2 |
| QUIZ_BOUNDARY_UNSUPPORTED | 3 |
| RUBRIC_TARGET_NOT_FOUND | 2 |
| **Total histórico** | **19** |

Os 19 registros foram agrupados por causa raiz: limites de quiz/revisão e cascata de gabaritos; resposta esperada de P2 com rótulo repetido; respostas físicas de 19.1 alinhadas por IDs explícitos; alvo de aceite de prática; nota instrucional sem alvo de exercício; e rubricas com lista compacta de alvos. A correção continua fail-closed em sequências incompletas, alvos ausentes/duplicados ou associações ambíguas.

## Correções e normalizações de representação

- Fronteiras de quiz são reconhecidas por estrutura literal e sequência declarada no manifesto; números como 404 não criam itens. Listas de revisão aceitam somente os marcadores previstos e IDs/ordem exatos.
- O arquivo de resposta esperada de 5.1/P2 preserva um corpo de solução com um único vínculo P2 apesar do rótulo repetido.
- As respostas de 19.1/Q2–Q3 são pareadas pelas linhas físicas e IDs explícitos; divergências de contagem/formato continuam bloqueantes.
- O aceite de 9.1/C01 é tipado como critério dirigido à prática P1; não é convertido em entrega fictícia.
- A nota de 23.3 é representada como `instructor_note` com audiência `instructor_only`, sem alvo inferido e sem projeção automática ao aluno.
- As rubricas de 27.3 e 27.4 resolvem P01, P02 e P03 na ordem declarada. A rubrica permanece canônica, sem cópia por alvo.
- A segmentação é transformação do contrato em memória. Não alterou Markdown, texto visível, enunciados, código, rubricas, escalas ou links na árvore persistida.

## Cobertura, proveniência e integridade

- Os 4.311 registros dos dez relatórios de migração apontam para 131 fontes distintas, todas existentes, e 2.879 destinos físicos únicos existentes.
- Dois registros são marcadores autorizados de remoção de relações duplicadas e não representam destino físico.
- Onze arquivos ficam fora dos destinos físicos dos relatórios: dez README estruturais da Fase 1 e `Fase_2/Projeto_incremental.md`. Os README da Fase 1 são convertidos como metadados/nós; o índice do projeto incremental permanece fora do contrato conforme decisão aprovada.
- O contrato contém 2.889 `SourceMapping`s para 2.889 arquivos. O único arquivo sem mapeamento é o índice estrutural do projeto incremental da Fase 2.
- Os 2.890 frontmatters YAML foram carregados com detecção de chaves duplicadas; os 2.890 `arquivo_id` são únicos. Não há arquivo vazio.
- Há 5.344 identidades de entidade no contrato (nós, blocos, relações, colocações, pendências, projetos, entregas e marcos); são únicas entre si e entre as fases. Validações não encontraram pais, relações ou destinos inexistentes.
- As 1.001 colocações apontam para blocos canônicos e assuntos existentes; não há pares bloco/assunto duplicados. A política de progresso continua como decisão de produto, sem bloquear a conversão.
- Fidelidade histórica: 2.746 arquivos com texto exato, 131 índices com metadados exatos, 12 arquivos antes bloqueados agora cobertos por parsing e testes de reconstrução literal, e um índice estrutural autorizado fora do contrato. Total: 2.890.

## Reprodutibilidade

Cada fase foi convertida duas vezes: uma na ordem declarada e outra com a ordem de solicitação das unidades invertida. Para as dez fases, contratos canônicos, mapeamentos (incluindo proveniência e hashes) e diagnósticos ordenados coincidiram byte a byte. Nenhum hash canônico divergiu.

| Fase | SHA-256 canônico |
|---|---|
| Fase 1 | `38d12a958c0bd31ec41f5b819068c15bcbcc6ad72fcf49943ddfc1f708256fa8` |
| Fase 2 | `d91e01cd719bc7e2535ece8c3747fd3fcee410bb615d7052b34edd82f2799055` |
| Fase 3 | `04864470f60e58e8c6f1a6767124860f93972fdeb1b972b605076481486ecd15` |
| Fase 4 | `d3b537bb193e1526bcd76c8557453f59a67030827949b9e757ba2be072a0c8b5` |
| Fase 5 | `5af9d81ee4ab283ed26fa90b45c1a8ddb46e70c4fa9deb5101148e763eb4e0dd` |
| Fase 6 | `d77aef39a55f85dc2418e89b508e579e15b7bd1fa207d92a4f8e36d799eea15b` |
| Fase 7 | `e7a7a5b04eea81d9d1ef43d0ab650bc431bd258875b7c5f7104d086a795b1a2e` |
| Fase 8 | `7a715fed692684048f9c6928d2e7d2a56ae27459debc59f14a03d4bbbe6517ee` |
| Fase 9 | `41a890c3d25c96b2d1b965c5cbfaf0807a71d2f65717032537ad8ad8008857ff` |
| Fase 10 | `c3901af3f8884d31230e025e21ea41b8cb5cf8bdaf9714317d783027039e83f1` |

As 94 ocorrências de wikilink continuam literais na árvore e a raiz do vault permanece não confirmada. A auditoria global anterior registrou 2.785 links Markdown relativos válidos; como os hashes da árvore conferem com o baseline auditado, esse resultado permanece aplicável. Esta execução não reescreveu nem tentou resolver links.

## Pendências editoriais e ressalvas

As 214 pendências atuais são classificadas por causa. A classificação preserva o texto e não inventa destinos:

| Causa | Quantidade |
|---|---:|
| Wikilink dependente da raiz do vault Obsidian | 66 |
| Wikilink literal sem alvo confirmado | 37 |
| Referência ao guia sem destino versionado | 17 |
| Relação curricular em prosa/conexão entre fases | 88 |
| Menção literal a 37.1/37.2 | 3 |
| Menção literal a 47.2/47.3 | 3 |
| **Total** | **214** |

As três menções a 37.1/37.2 e as três a 47.2/47.3 são referências literais sem destino confirmado. Não são evidência, por si só, de conflito de versões. As cópias editoriais 37.1/37.2 permanecem preservadas; não foram movidas nem fundidas. Não há objetos `editorial_transfer` ou `source_version_conflict` entre essas 214 pendências. Separadamente, há 597 referências externas, dez referências editoriais e um wikilink tipado em `ReferenceBlock`. A raiz Obsidian e o escopo do progresso em conteúdo compartilhado continuam ressalvas.

## Dependências de desenvolvimento

A resolução de `backend/requirements-dev.txt` foi tentada com `uv pip compile`, usando um caminho temporário recém-criado e removido ao fim. O resolver falhou: `google-api-core==2.33.0` requer `grpcio-status>=1.75.1,<2`, enquanto `backend/requirements.txt` fixa `grpcio-status==1.71.2`; `google-ai-generativelanguage==0.6.15` também depende de `google-api-core[grpc]`. Não há lockfile ou arquivo de constraints encontrado. Nenhuma dependência foi alterada.

Ambiente: Python 3.13.15, Pydantic 2.13.5, PyYAML 6.0.3, pytest 9.1.1, Ruff 0.17.1, mypy 2.4.0. Os testes direcionados passaram no ambiente já disponível apesar do conflito de resolução.

## Testes e verificações

| Verificação | Resultado |
|---|---|
| `py -3.13 -m pytest -q backend/unit_tests/test_curriculum_contract.py backend/unit_tests/test_curriculum_markdown_converter.py backend/unit_tests/test_import_payload_shape.py --tb=short` | **97 passaram**. Abrange regressões 12A, 12B, 12B.1 e payload relevante; a 12C foi exercitada pelo dry-run em memória. |
| `ruff check backend/curriculum_contract backend/unit_tests/test_curriculum_contract.py backend/unit_tests/test_curriculum_markdown_converter.py` | Aprovado. |
| `ruff format --check backend/curriculum_contract backend/unit_tests/test_curriculum_contract.py backend/unit_tests/test_curriculum_markdown_converter.py` | Aprovado; seis arquivos já formatados. |
| `mypy --explicit-package-bases curriculum_contract unit_tests/test_curriculum_contract.py unit_tests/test_curriculum_markdown_converter.py --show-error-codes --no-incremental --disable-error-code=import-untyped` em `backend/` | Aprovado; seis arquivos. Supressão limitada à ausência de stubs de PyYAML. |
| `py -3.13 -m compileall -q backend/curriculum_contract` e `git diff --check` | Aprovados. |
| Conversão duas vezes por fase em ordem direta e invertida; YAML com chaves únicas; validação semântica | Aprovados; 20 conversões, zero erros. |

## Relatórios produzidos

- `docs/migracao/RELATORIO_ETAPA_12C1.md`
- `docs/migracao/DIAGNOSTICOS_12C1.csv` — 1.225 diagnósticos atuais estruturados; zero com severidade `error`.
- `docs/migracao/COBERTURA_CONVERSAO_12C1.csv` — 2.890 linhas, uma por arquivo migrado, com caminho, ID, hash, mapeamento, tipos e estado de cobertura.

Os resultados históricos da 12C não foram alterados.

## Git e recomendação

O checkout permanece na branch `migracao-estrutura` e HEAD `147dc68b81169f66b0ba3802fa2f26e5130923a3`. O índice continua vazio e nenhum arquivo rastreado foi alterado. Somente os três relatórios desta etapa foram criados nesta rodada; os artefatos locais preexistentes foram preservados. Não houve commit, geração de JSON, importador ou acesso ao MongoDB.

**Parecer:** os bloqueios de conversão do contrato foram resolvidos; a conversão em memória das dez fases é reproduzível e rastreável, sem perda reportada. Recomendo homologar a 12C.1 e, mediante autorização própria, prosseguir para conversão integral persistida do contrato intermediário. Isso ainda não autoriza JSON definitivo nem importação na plataforma: compatibilidade de `answer_key`/conteúdo instrucional, política de revelação de respostas, progresso compartilhado e referências editoriais/vault exigem gates separados.
