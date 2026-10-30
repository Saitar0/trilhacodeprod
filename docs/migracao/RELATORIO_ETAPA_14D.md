# Relatório — Etapa 14D: recuperação estrutural e persistência privada de quizzes

## Resultado

**Concluída parcialmente para homologação.** A auditoria classificou as 359 questões que estavam bloqueadas na 14C. Uma delas voltou a ser candidata após corrigir uma comparação de texto que tratava diferenças de caixa como duplicidade. Os 142 candidatos anteriores foram preservados. Permanecem 358 itens bloqueados, e nenhum candidato foi publicado ou persistido.

## Pré-voo e preservação

- Worktree: `C:\Users\Joao\.codex\worktrees\fase1-migracao\trilhacodeprod`.
- Branch/HEAD: `migracao-estrutura` / `147dc68b81169f66b0ba3802fa2f26e5130923a3`.
- Índice Git vazio no início e no fim. O worktree já continha alterações rastreadas e não rastreadas de etapas anteriores; elas foram preservadas.
- Bundle curricular: SHA-256 `43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2`, igual antes e depois.
- CSV histórico da 14C: SHA-256 `bd8487357aab3e6aa6b4831362ee52b88fa230d1f78c1bc136ae95be60fab89b`, igual antes e depois.
- Nenhuma árvore curricular, contrato intermediário, JSON, modelo de produção, banco ou configuração operacional foi alterado nesta etapa.

## Cobertura e reconciliação

O bundle contém 501 questões que exigem gabarito e cinco perguntas R1–R5 sem gabarito. As cinco perguntas sem chave continuam fora do corretor e da pontuação.

| Estado | 14C | 14D | Variação |
| --- | ---: | ---: | ---: |
| Candidatas estruturais | 142 | 143 | +1 |
| Bloqueadas por alternativas/formato | 348 | 347 | -1 |
| Bloqueadas por gabarito | 11 | 11 | 0 |
| Perguntas sem gabarito, sem nota | 5 | 5 | 0 |

Os 359 bloqueios da 14C reconciliam para **1 questão recuperada + 358 ainda bloqueadas**. Os 142 candidatos anteriores continuam candidatos; não houve regressão. A correspondência completa por `phase + quiz_ref`, com status anterior e atual, está em [CLASSIFICACAO_QUIZZES_14D.csv](CLASSIFICACAO_QUIZZES_14D.csv). O arquivo contém 501 linhas de questões com chave, incluindo os 142 casos de controle.

### Classificação dos 359 bloqueios anteriores

| Classificação em 14D | Quantidade | Situação |
| --- | ---: | --- |
| Múltipla escolha recuperável | 1 | Diferença entre `String` e `string` foi preservada; gabarito por letra foi inequívoco. |
| Múltipla escolha incompleta | 1 | A fonte diz “Múltipla escolha”, mas não fornece alternativas. |
| Resposta aberta | 314 | Perguntas textuais sem opções; fora do corretor atual. |
| Exercício discursivo | 23 | A fonte pede justificativa, explicação, comparação ou produção textual. |
| Pergunta de revisão | 1 | A seção de origem identifica uma questão como revisão. |
| Tipo não representável pelo avaliador atual | 8 | Quatro tarefas de associação e quatro de ordenação; o CSV conserva o sinal de formato específico. |
| Ambiguidade de gabarito | 11 | Alternativas explícitas, mas a chave não identifica uma opção única. |
| **Total dos bloqueios de 14C** | **359** | **1 recuperada + 358 ainda bloqueadas.** |

“Tipo não representável pelo avaliador atual” usa a categoria de auditoria `unidentified`: a fonte permite reconhecer associação ou ordenação, mas o corretor vigente não tem esses formatos. Isso não os converte em múltipla escolha.

## Auditoria das fontes e dos formatos

As 501 questões e chaves continuam com `format=other` e `options=[]` no bundle. A conversão depende, portanto, de evidência no Markdown, e não de campos tipados de alternativas.

- As 501 linhas de questão foram localizadas nas páginas originais de 101 unidades; cada registro tem caminho e número de linha.
- As 501 chaves foram rastreadas até o texto de origem sem incluí-lo no CSV: 138 respostas inline com rótulo explícito, cinco entradas numeradas em seção de gabarito e 358 correspondências textuais únicas.
- Nos 359 bloqueios históricos, havia um ordinal numerado de questão por bloco; nenhum tinha uma segunda lista numerada que comprovasse alternativas numéricas. O parser não interpreta o ordinal como opções.
- Entre esses 359 blocos, 12 apresentavam marcadores de opção: 11 com chave não mapeável e o item recuperado após a correção de caixa. Um bloco adicional tinha rótulo explícito de múltipla escolha, sem opções.
- Não foram encontrados quadros Markdown, checklists ou blocos de código cercados usados como alternativas nesses 359 blocos. Código inline aparece em 68 deles como parte do enunciado e não foi interpretado como alternativa.
- Foram mantidas as regras existentes para listas/letras A–D, marcadores inline explícitos e exclusão de conteúdo dentro de código. Não foi adicionada regra para listas numeradas, tabelas ou checklists porque as fontes examinadas não forneceram alternativas avaliáveis inequívocas nesses formatos.

### Onze chaves não mapeáveis

Os vínculos de cada chave com seu quiz estão consistentes. Em todas as 11 ocorrências, não há `correct_option_ref`; o valor de resposta não é um rótulo A–D inequívoco nem corresponde textualmente a uma única alternativa. A fonte não permite distinguir com segurança uma resposta discursiva de uma explicação ou de outra referência incompleta, então todas continuam bloqueadas. Não foi identificada associação cruzada com outra questão nem contradição estrutural comprovada.

IDs: `f5-19-2-01-requisito-e-escolha-de-abstracao-02-quiz-question-q1`, `f5-20-2-01-armazenamento-de-senhas-02-quiz`, `f5-20-3-02-propriedades-e-minimizacao-02-quiz`, `f5-21-1-03-di-ponto-de-composicao-02-quiz-question-q3`, `f7-32-1-01-workflow-reprodutibilidade-quality-gates-q01-quiz-md`, `f7-32-2-01-identidade-do-artefato-q01-quiz-md`, `f7-33-1-01-modelos-mensageria-entrega-q02-quiz-md`, `f7-34-1-02-vpc-subnets-rotas-security-groups-q01-quiz-md`, `f7-35-1-02-filas-pubsub-event-routing-q01-quiz-md`, `f7-36-1-03-plano-segredos-aprovacao-q02-quiz-md` e `f7-36-2-01-ambientes-state-isolamento-q02-quiz-md`. O CSV registra origem, bloco e diagnóstico por ocorrência, sem texto de gabarito.

## Mudança conservadora do parser

O parser anteriormente comparava o texto das opções após `casefold()`. Isso tratou `String` e `string` como duplicatas, embora sejam valores distintos no exemplo de código da fonte. A comparação agora normaliza apenas espaços, preservando caixa e pontuação. Duplicatas textuais realmente idênticas continuam bloqueadas.

Nenhuma alternativa, resposta ou explicação foi criada. Não foi aplicada conversão sem evidência. As cinco perguntas R1–R5 sem chave continuam não pontuadas.

## Compatibilidade com o avaliador existente

O corretor em `backend/services/quizzes.py` aceita questões com alternativas, uma `correct_option_id` existente e respostas por `option_id`. Ele rejeita quiz vazio, opções inválidas e tipos fora de múltipla escolha. A nota é uniforme por questão, usa comparação exata com o limiar de 70% e não arredonda antes da decisão. A política de três tentativas, melhor nota e revisão após a terceira continua no serviço existente.

Os 143 casos são **candidatas estruturais em memória**, não quizzes publicáveis. O conversor ainda não resolve refs curriculares para IDs internos da versão Mongo, nem persiste chaves privadas. Nenhum endpoint, modelo, índice, migração ou avaliador foi modificado.

## Persistência privada

A especificação proposta está em [CONTRATO_PERSISTENCIA_PRIVADA_QUIZZES.md](CONTRATO_PERSISTENCIA_PRIVADA_QUIZZES.md). Ela recomenda versões imutáveis com projeção pública separada da chave privada, hash canônico cobrindo ambas, proveniência por bloco e publicação somente após validação e revisão editorial. A política de armazenamento é uma recomendação; não foi implementada nem aprovada como alteração de produção.

## Testes e verificações

Ambiente: Windows, Python 3.13; sem serviço, banco ou rede iniciados.

- `py -3.13 -m pytest unit_tests/test_experimental_quiz_converter.py unit_tests/test_quiz_grading.py unit_tests/test_curriculum_bulk_import.py -q` — **41 testes aprovados** após as alterações desta etapa.
- `ruff check` e `ruff format --check` nos arquivos Python da 14D — aprovados.
- mypy focado no conversor, auditor e teste — aprovado, três arquivos.
- `py_compile` do conversor, auditor e teste — aprovado.
- `git diff --check` — sem erros de whitespace; o Git avisou que o JSON preexistente marcado como modificado poderá converter LF para CRLF ao ser escrito pelo Git. O hash do JSON permanece o esperado e o arquivo não foi escrito nesta etapa.
- Nenhum teste acessou MongoDB, importador ou publicação. O CSV foi regenerado pelo conversor e comparado com sua serialização determinística; os bytes da 14C foram apenas lidos para a reconciliação.

## Decisões e pendências

- Os 11 gabaritos ambíguos precisam de esclarecimento editorial; nenhum foi escolhido por aproximação.
- A questão de 46.1 sem alternativas exige completar a fonte ou aprovar outro tipo de resposta, se desejado.
- Respostas abertas, discursivas, associação e ordenação necessitam de decisão de produto e possível extensão do avaliador; nenhuma resposta automática foi criada.
- As políticas da 14C sobre progresso compartilhado, R1–R5, projeto, relações e referências continuam pendentes.
- Não há persistência privada implantada; os candidatos da 14D não podem ser publicados.

## Arquivos desta etapa

- Modificado: `backend/curriculum_contract/experimental_quiz_converter.py` — comparação de opções sensível a caixa.
- Modificado: `backend/unit_tests/test_experimental_quiz_converter.py` — regressões de distinção de caixa, preservação dos 142 candidatos, classificação e procedência.
- Criado: `backend/curriculum_contract/quiz_structure_audit.py` — classificação offline por ID, verificação de origem e CSV sem conteúdo de gabarito.
- Criado: `backend/unit_tests/fixtures/quiz_formats_14d.json` — oito trechos reais somente de enunciado, sem chaves ou explicações.
- Criados: `CLASSIFICACAO_QUIZZES_14D.csv`, `CONTRATO_PERSISTENCIA_PRIVADA_QUIZZES.md` e `COMPARATIVO_CONVERSAO_14C_14D.md`.
- Criado: este relatório.

**Parecer:** protótipo offline aprovado para revisão técnica. A cobertura avaliativa permanece parcial: 358 questões continuam bloqueadas. Persistência, publicação e decisões editoriais dependem de homologação posterior.
