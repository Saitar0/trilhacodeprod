# Relatório — Etapa 14C: protótipo offline de conversão de quizzes

## Resultado

**Concluída parcialmente para homologação do protótipo.** Foram analisados os 501 quizzes que declaram gabarito. O conversor criou em memória candidatos compatíveis com a estrutura de questão do backend somente quando alternativas, ordem e resposta puderam ser associados sem inferência. Os candidatos não foram persistidos, publicados nem agrupados em versões de banco.

## Pré-voo e preservação

- Worktree: `C:\Users\Joao\.codex\worktrees\fase1-migracao\trilhacodeprod`.
- Branch/HEAD: `migracao-estrutura` / `147dc68b81169f66b0ba3802fa2f26e5130923a3`.
- Índice Git vazio antes da execução. O worktree já tinha alterações rastreadas e não rastreadas; foram preservadas.
- Pacote lido: `docs/courses/trilhacode/trilha-code-bulk-import.json`.
- SHA-256 conferido antes e depois: `43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2`.
- A leitura usou `CurriculumImportBundle` e os blocos tipados do pacote. Nenhuma conexão ao MongoDB, endpoint de publicação ou importador foi usada.
- O JSON, os modelos de produção, o contrato intermediário e as árvores migradas não foram modificados nesta etapa.

## Cobertura

O bundle contém 506 blocos `quiz`: 501 declaram gabarito associado e cinco são perguntas R1–R5 sem gabarito. Os 501 gabaritos apontam para questões existentes; 99 têm explicação original e nenhuma chave usa `accepted_answers`. Os 501 quizzes avaliáveis têm `format=other` e `options=[]`; a análise não presumiu que um texto qualquer seja múltipla escolha. Explicações existentes são preservadas como opcionais, sem gerar explicações para as demais questões.

| Resultado da análise | Quantidade | Detalhe |
|---|---:|---|
| Candidato convertido sem ambiguidade | 142 | 137 com quatro alternativas e cinco com três; todos os marcadores seguem ordem explícita e o gabarito aponta para uma alternativa única. |
| Bloqueado por alternativas | 348 | 347 sem marcadores explícitos de alternativas; um contém texto de alternativas duplicado. |
| Bloqueado por gabarito | 11 | O texto do gabarito não identifica exatamente uma alternativa; nenhuma correspondência por semelhança foi tentada. |
| Bloqueado por enunciado | 0 | Nenhum candidato que chegou a uma extração válida tinha stem vazio; não se completou stem algum. |
| Bloqueado por incompatibilidade de schema/corretor por questão | 0 | Os 142 candidatos passaram os validadores de questão e o corretor puro. Isso não significa que possam ser publicados/importados. |
| Outras causas | 0 | Nenhum fallback foi aplicado. |
| Perguntas sem gabarito, fora do total de 501 | 5 | Mantidas como `unscored_review_pending`; não viraram avaliações. |

Total das 501 questões com chave: `142 + 348 + 11 = 501`. A cobertura linha a linha, com IDs e proveniência e sem texto de resposta/explicação, está em [COBERTURA_CONVERSAO_QUIZZES_14C.csv](COBERTURA_CONVERSAO_QUIZZES_14C.csv). O CSV tem 506 registros para que as cinco perguntas sem chave também permaneçam rastreáveis.

### Perguntas sem gabarito

R1–R5 pertencem a `Fase_4/16.3_Projeto_de_fase_Trilho_B/01_projeto_trilho_b/Q01_revisao_decisoes.md`. O protótipo as classifica como `unscored_review_pending`, mantém ID, arquivo, SHA de origem e `answer_key_present=no`, e não cria resposta, pontuação ou explicação. Alternativas para decisão editorial: preservar como revisão formativa sem nota, ou decidir um fluxo de revisão humana separado. Nenhuma alternativa foi aplicada.

## Compatibilidade e privacidade

- Cada candidato validado usa a allowlist real `QuizQuestionOut`: `question_id`, `order`, `prompt` e `options`. Resposta correta e explicação não aparecem em `public_payload()`.
- O gabarito fica num objeto privado separado; seu `repr` e o CSV não incluem resposta ou explicação. A versão SHA-256 inclui o conteúdo avaliativo apenas em memória e não é emitida no relatório/CSV.
- Os 142 candidatos passaram `backend/services/quizzes.py::_question_snapshot` e `grade_quiz_questions` em testes offline. O identificador ObjectId usado no teste é sintético e efêmero; o protótipo não cria nem reserva IDs Mongo.
- A regra de 70% e a correção autoritativa permanecem no corretor existente. Os testes de regressão desse serviço passaram; não houve tentativa, persistência de histórico ou verificação de política de revelação nesta etapa.
- O fluxo completo de publicação continua incompatível: falta o mapeamento autorizado de refs curriculares para IDs internos de nós/blocos e um caminho de persistência privada/versionada para a chave. Portanto, **nenhum dos 142 candidatos é publicável** por este protótipo.
- Os 11 gabaritos não mapeáveis e 348 itens sem alternativas explícitas continuam bloqueados. O protótipo não transforma resposta textual em alternativa, não inventa explicação e não usa IA.

Exemplo sanitizado de diagnóstico: `converted_candidate / UNAMBIGUOUS_MULTIPLE_CHOICE_CANDIDATE` significa que a estrutura de alternativas e a chave têm associação única; o relatório não inclui o marcador correto nem texto da chave. `blocked_alternatives / ALTERNATIVES_NOT_EXPLICIT` significa que o texto não foi reinterpretado como opções.

## Decisões curriculares

As seis políticas da matriz permanecem pendentes: progresso compartilhado; tratamento das cinco perguntas sem chave; modelo de projetos; subtipo para 34 relações rotuladas como pré-requisito; relação ambígua “pré-requisito/revisita”; e destino de 11 referências. As recomendações técnicas não foram aplicadas. Ver [MATRIZ_APROVACAO_POLITICAS_14C.md](MATRIZ_APROVACAO_POLITICAS_14C.md) e a matriz individual das relações em [MATRIZ_DECISOES_CURRICULARES.md](MATRIZ_DECISOES_CURRICULARES.md).

## Testes e verificações

Ambiente: Windows, Python 3.13, Pydantic instalado no runtime de testes; sem serviços iniciados e sem banco.

- `py -3.13 -m pytest unit_tests/test_experimental_quiz_converter.py unit_tests/test_quiz_grading.py unit_tests/test_curriculum_bulk_import.py -q` — **35 passaram**.
- `ruff check curriculum_contract/experimental_quiz_converter.py unit_tests/test_experimental_quiz_converter.py` — passou.
- `ruff format --check curriculum_contract/experimental_quiz_converter.py unit_tests/test_experimental_quiz_converter.py` — passou.
- `py -3.13 -m mypy --follow-imports=silent --explicit-package-bases --namespace-packages curriculum_contract/experimental_quiz_converter.py unit_tests/test_experimental_quiz_converter.py` — passou para os dois arquivos do protótipo.
- `py -3.13 -m py_compile curriculum_contract/experimental_quiz_converter.py unit_tests/test_experimental_quiz_converter.py` — passou.
- Teste com importações completas do mypy também foi executado; encontrou 13 erros fora dos arquivos desta etapa, em `database.py`, `audit.py`, `services/auth.py`, `services/common.py`, `learning.py` e `integrity.py`. Não há erro nos dois arquivos do protótipo; o mypy focado com imports silenciados passou.
- O bundle foi validado como JSON tipado e sua SHA permaneceu idêntica. A matriz e o CSV não contêm respostas nem explicações.

## Parecer e próxima etapa

**Protótipo offline aprovado tecnicamente para revisão, não para publicação.** 142 questões podem ser convertidas estruturalmente com evidência explícita; 359 das 501 permanecem bloqueadas. Antes de qualquer conversão operacional, é necessário decidir a política para as cinco revisões sem chave e o tratamento dos formatos textuais, além de implementar e homologar a persistência privada/versionada e o mapeamento de IDs internos. As políticas de progresso, projetos, relações e referências continuam sem aprovação e não foram alteradas. Nenhuma importação ou commit foi realizado.
