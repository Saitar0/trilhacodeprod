# Relatório da Etapa 12C — Dry-run global do contrato intermediário

## Resultado

**Veredito: NÃO PRONTO PARA CONVERSÃO INTEGRAL.** As dez fases foram convertidas em memória sem escrita curricular, JSON, banco ou uso do importador. Os textos permanecem na árvore; os bloqueios são lacunas na representação pelo contrato.

- Worktree: checkout isolado informado para esta execução.
- Branch: migracao-estrutura
- HEAD: 147dc68b81169f66b0ba3802fa2f26e5130923a3
- Versão do contrato: trilhacode.intermediate/1.1
- Arquivos Markdown migrados: 2890
- Unidades: 131
- Projetos: 15
- Linhas de mapeamento dos CSVs: 4311
- Destinos físicos únicos: 2879, todos existentes
- Linhas sem destino por remoções autorizadas de relações duplicadas: 2
- Arquivos estruturais fora dos destinos CSV: 11
- SourceMappings produzidos: 2878 em 2878 caminhos
- Entidades incluindo entregas, marcos e variações: 5298
- Blocos: 3401; colocações compartilhadas: 985
- Diagnósticos: 19 erros, 66 avisos, 1137 informações
- Fidelidade textual/metadados comprovada: 2877 arquivos; bloqueados: 12; estruturais autorizados fora do contrato: 1

## Reconciliação

A árvore tem 2.890 Markdown; os CSVs de migração somam 4.311 registros, com 2.879 destinos físicos únicos. Dois registros usam o marcador aprovado de relação duplicada sem destino. Os outros destinos existem.

Arquivos estruturais fora dos destinos físicos:

- docs/courses/trilhacode/Conteudos_migrado/Fase_1/1.1_Computacao_e_software/README.md.
- docs/courses/trilhacode/Conteudos_migrado/Fase_1/1.2_Ambiente_de_desenvolvimento/README.md.
- docs/courses/trilhacode/Conteudos_migrado/Fase_1/2.1_Terminal_e_navegacao/README.md.
- docs/courses/trilhacode/Conteudos_migrado/Fase_1/2.2_Sistema_e_operacao/README.md.
- docs/courses/trilhacode/Conteudos_migrado/Fase_1/2.3_Acesso_remoto/README.md.
- docs/courses/trilhacode/Conteudos_migrado/Fase_1/3.1_Git_local/README.md.
- docs/courses/trilhacode/Conteudos_migrado/Fase_1/3.2_Trabalho_com_historico/README.md.
- docs/courses/trilhacode/Conteudos_migrado/Fase_1/3.3_GitHub/README.md.
- docs/courses/trilhacode/Conteudos_migrado/Fase_1/3.4_Revisita_continua/README.md.
- docs/courses/trilhacode/Conteudos_migrado/Fase_1/3.5_Projeto_incremental/README.md.
- docs/courses/trilhacode/Conteudos_migrado/Fase_2/Projeto_incremental.md.

Os dez README da Fase 1 são índices/metadados; Projeto_incremental.md na Fase 2 é índice de práticas já existentes e fica fora dos nós do contrato conforme decisão aprovada. Não foram criados arquivos artificiais.

## Contagens por fase

Colunas: fase, unidades, arquivos, registros CSV, destinos CSV, SourceMappings, nós, blocos, projetos, colocações, relações, pendências, erros, avisos e informações.

| Fase | Unid. | Arqs. | CSV | Dest. | Maps | Nós | Blocos | Proj. | Coloc. | Rel. | Pend. | Erros | Avisos | Info |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Fase_1 | 10 | 221 | 272 | 211 | 221 | 43 | 263 | 1 | 95 | 21 | 32 | 0 | 22 | 106 |
| Fase_2 | 7 | 144 | 209 | 143 | 142 | 27 | 188 | 0 | 95 | 9 | 15 | 1 | 10 | 101 |
| Fase_3 | 14 | 313 | 581 | 313 | 309 | 60 | 362 | 2 | 202 | 25 | 48 | 10 | 27 | 224 |
| Fase_4 | 17 | 395 | 635 | 395 | 393 | 77 | 502 | 2 | 201 | 0 | 19 | 2 | 1 | 220 |
| Fase_5 | 20 | 483 | 762 | 483 | 481 | 88 | 614 | 2 | 113 | 0 | 22 | 4 | 1 | 135 |
| Fase_6 | 20 | 449 | 616 | 449 | 447 | 85 | 499 | 2 | 88 | 0 | 23 | 2 | 1 | 111 |
| Fase_7 | 7 | 156 | 210 | 156 | 156 | 36 | 181 | 0 | 25 | 0 | 8 | 0 | 1 | 33 |
| Fase_8 | 8 | 124 | 192 | 124 | 124 | 25 | 143 | 2 | 15 | 0 | 11 | 0 | 1 | 26 |
| Fase_9 | 16 | 301 | 428 | 301 | 301 | 71 | 331 | 2 | 123 | 0 | 19 | 0 | 1 | 142 |
| Fase_10 | 12 | 304 | 406 | 304 | 304 | 60 | 318 | 2 | 28 | 0 | 17 | 0 | 1 | 45 |

Totais: 572 nós (module=53, phase=10, submodule=131, topic=378), 3401 blocos, 15 projetos, 20 entregas, 36 marcos formais, 0 variações, 985 colocações compartilhadas, 55 relações e 214 pendências editoriais.

### Blocos por tipo

| Tipo | Quantidade |
|---|---|
| acceptance_criteria | 16 |
| answer_key | 491 |
| checklist | 89 |
| completion_criteria | 130 |
| feedback | 179 |
| flashcard | 45 |
| objective | 131 |
| practice | 327 |
| project_decision | 1 |
| project_review | 1 |
| project_scenario | 1 |
| quiz | 493 |
| reference | 608 |
| rubric | 176 |
| solution | 211 |
| summary | 123 |
| theory | 379 |

## Fidelidade textual

Os corpos de teoria, objetivo, resumo, critérios, práticas, soluções, feedback, rubricas, checklists, escopos, entregas e marcos foram comparados com os campos tipados. Para quiz e gabaritos, segmentos em ordem foram concatenados e comparados ao corpo integral. Referências e conexões foram conferidas linha a linha com registros de mesma origem. Os frontmatters completos dos README foram comparados aos metadados dos nós. SHA-256 da fonte foi conferido para cada SourceMapping.

Resultado: 2746 corpos exatos, 131 README com metadados exatos, 1 índice estrutural fora da conversão e 12 arquivos bloqueados. Foram encontrados 94 wikilinks; 94 aparecem literalmente em campos do contrato por mesma origem. Ocorrências não representadas: 0.

Arquivos bloqueados:

- docs/courses/trilhacode/Conteudos_migrado/Fase_2/5.1_Base_visual/90_integracao/02_resposta_esperada_pratica_independente.md: ANSWER_BOUNDARY_UNSUPPORTED.
- docs/courses/trilhacode/Conteudos_migrado/Fase_3/7.3_Dados_e_comunicacao/02_requisicao_async_resposta_erros/02_quiz.md: QUIZ_BOUNDARY_UNSUPPORTED.
- docs/courses/trilhacode/Conteudos_migrado/Fase_3/7.3_Dados_e_comunicacao/02_requisicao_async_resposta_erros/03_gabarito_quiz.md: ANSWER_QUESTION_NOT_SELECTED.
- docs/courses/trilhacode/Conteudos_migrado/Fase_3/7.5_Depuracao_no_navegador/02_network_requisicoes/02_quiz.md: QUIZ_BOUNDARY_UNSUPPORTED.
- docs/courses/trilhacode/Conteudos_migrado/Fase_3/7.5_Depuracao_no_navegador/02_network_requisicoes/03_gabarito_quiz.md: ANSWER_QUESTION_NOT_SELECTED.
- docs/courses/trilhacode/Conteudos_migrado/Fase_4/16.3_Projeto_de_fase_Trilho_B/01_projeto_trilho_b/Q01_revisao_decisoes.md: QUIZ_BOUNDARY_UNSUPPORTED.
- docs/courses/trilhacode/Conteudos_migrado/Fase_4/9.1_Conceitos/90_integracao/C01_criterios_aceite.md: PROJECT_ACCEPTANCE_TARGET_MISSING.
- docs/courses/trilhacode/Conteudos_migrado/Fase_5/19.1_ORM_e_acesso_a_dados/02_consultas_relacoes_custo/02_quiz.md: QUIZ_ANSWER_KEY_MISSING.
- docs/courses/trilhacode/Conteudos_migrado/Fase_5/19.1_ORM_e_acesso_a_dados/02_consultas_relacoes_custo/03_gabarito_quiz.md: ANSWER_BOUNDARY_UNSUPPORTED.
- docs/courses/trilhacode/Conteudos_migrado/Fase_5/23.3_Regra_dura/Nota_do_instrutor.md: INSTRUCTOR_NOTE_TARGET_UNRESOLVED.
- docs/courses/trilhacode/Conteudos_migrado/Fase_6/27.3_Contrato_de_dados/90_integracao/RUB_rubrica_praticas.md: RUBRIC_TARGET_NOT_FOUND.
- docs/courses/trilhacode/Conteudos_migrado/Fase_6/27.4_Seguranca_no_navegador/90_integracao/RUB_rubrica_praticas.md: RUBRIC_TARGET_NOT_FOUND.

A validação agregada também detectou dois erros de gabarito ausente em Q2/Q3 de 19.1. Eles correspondem a diagnósticos já presentes na conversão da Fase 5 e não foram contados novamente; nenhum erro adicional exclusivo da validação agregada foi encontrado.

## Diagnósticos

| Código | Ocorrências |
|---|---|
| ANSWER_BOUNDARY_UNSUPPORTED | 2 |
| ANSWER_QUESTION_NOT_SELECTED | 8 |
| EDITORIAL_PENDING_RECORDED | 142 |
| INSTRUCTOR_NOTE_TARGET_UNRESOLVED | 1 |
| NODE_STATUS_TRANSLATED | 10 |
| OBSIDIAN_ROOT_UNCONFIRMED | 66 |
| PROJECT_ACCEPTANCE_TARGET_MISSING | 1 |
| QUIZ_ANSWER_KEY_MISSING | 2 |
| QUIZ_BOUNDARY_UNSUPPORTED | 3 |
| RUBRIC_TARGET_NOT_FOUND | 2 |
| SHARED_PROGRESS_SCOPE_UNDECIDED | 985 |

Os avisos sobre raiz do vault Obsidian permanecem. A política de progresso das colocações compartilhadas também depende de decisão de produto.

## Reprodutibilidade

Cada fase foi convertida duas vezes, com ordem de solicitação das unidades oficial e invertida. Objetos, mappings, diagnósticos e SHA canônico coincidiram nas dez fases.

| Fase | SHA-256 do contrato canônico |
|---|---|
| Fase_1 | 86a02503aa9524381a32c86e09e0c46bea25d1a4e0858f1bf6e8d576c9a644de |
| Fase_2 | e0e6c539249a2a367f599dfef770353f9830917355f641ca20fced9389ce5934 |
| Fase_3 | 6052ea300e60bd8822cc03665d12335dbebeb79edff823ffd803332ee19cb0a6 |
| Fase_4 | e39f64b9b4836cca8751e18b4a6a2b24ad9023712bf9352a5a44e3e006d7efa8 |
| Fase_5 | 52b6877318a5c42f6d4b12993075d6e045b1fbafb657b57e5a541bb7a1cd8c1e |
| Fase_6 | 5668fdf58a13e9d6950886cb0714be7342c0762cfad17c3fa1bfa94dbecb2c2c |
| Fase_7 | 1c245eba3ce58b5cf1b1c9d51ad6987becb5c2155336b23cb724d08069ba0496 |
| Fase_8 | 55ce39aac99b9d26fee07c4d1aa57880e55665ad929a0f83a15273a76d1cdb39 |
| Fase_9 | 5f67cdbaee338591df857f0574819213c1728db65a06e570bc22305af1ae4e26 |
| Fase_10 | 856e638c7eda24ec306e09280895d99423145bc9a1a319b05c381cd31e9f6ba5 |

A serialização não inclui campos voláteis. A conversão foi em memória; nenhum diretório temporário foi criado.

## Referências e ressalvas editoriais

- A auditoria global anterior registra 2.785 links Markdown relativos válidos; esta execução não reescreveu links.
- Os wikilinks foram preservados; a raiz do vault permanece não confirmada.
- As referências textuais a 47.2/47.3 continuam sem destino ativo confirmado.
- As cópias editoriais 37.1/37.2 não foram selecionadas nem alteradas.
- O índice de projeto incremental da Fase 2 não virou nó do contrato, conforme decisão aprovada.

## Testes

- Testes 12A, 12B, 12B.1 e regressão de payload: 84 aprovados.
- Ruff, Ruff format --check, mypy e compilação Python: aprovados.
- A resolução de backend/requirements-dev.txt falhou por conflito entre versões travadas de google-api-core, grpcio-status e dependências Google. Os testes direcionados passaram em ambiente efêmero com dependências mínimas explícitas.
- A auditoria de links global foi reutilizada; nenhuma árvore foi modificada.

## Integridade e Git

- Markdown original em Conteudos/: 133 arquivos presentes.
- JSON legado SHA-256: 43125c5902168def6359e514ad80602a1f7579157e1a0bb16f1f2212ee4c18e7; igual ao hash-base verificado.
- Branch/HEAD preservados; índice vazio; sem commit, importador ou MongoDB.
- Relatórios criados: RELATORIO_ETAPA_12C.md, DIAGNOSTICOS_12C.csv e COBERTURA_CONVERSAO_12C.csv.
- Ajuste do conversor: conexões em prosa ficam como pendências literais, sem destino inferido; pendências e relações de conexões têm referências registradas no SourceMapping. Teste novo aprovado.
- Árvore curricular inalterada. Backups não encontrados não são declarados verificados.

## Parecer

O conversor é reproduzível, com texto exato demonstrado em 2877 arquivos. Não está pronto para conversão integral homologada: 19 erros bloqueantes atingem 12 arquivos. É necessário tratar fronteiras de quizzes/gabaritos e alvos de critérios, rubricas e nota do instrutor com regras explícitas. Permanecem a política de progresso compartilhado e a raiz do vault como pendências.
