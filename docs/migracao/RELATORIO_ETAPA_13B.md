# Relatório — Etapa 13B: fluxo seguro de quizzes

## Resultado

Foi documentado um fluxo proposto para separar leitura pública, envio de tentativa, resultado, histórico e correção administrativa. Foi criado um conjunto isolado de testes contratuais, usando os modelos reais de quiz e gabarito do contrato intermediário e um simulador em memória.

Nenhum endpoint, schema de produção, renderer, banco de dados, JSON, importador ou contrato intermediário foi alterado. Não houve commit.

## Pré-voo e integridade

- Worktree: C:/Users/Joao/.codex/worktrees/fase1-migracao/trilhacodeprod
- Branch: migracao-estrutura
- HEAD: 147dc68b81169f66b0ba3802fa2f26e5130923a3
- O índice estava vazio e não havia diferenças em arquivos rastreados.
- Os arquivos locais não rastreados foram preservados.
- Os artefatos do contrato intermediário da Etapa 12D permaneceram presentes. SHA-256 do manifesto: c3f5aa792641408eb66fc80cf801206de4e1deef2130a5a5c436c8d9ade58055.
- A árvore curricular com 2.890 arquivos permaneceu sem alteração.
- O JSON legado permaneceu sem alteração; SHA-256 de referência e verificado: 43125c5902168def6359e514ad80602a1f7579157e1a0bb16f1f2212ee4c18e7.

A checagem inicial no terminal restrito não conseguiu acessar a área administrativa do worktree. A execução local autorizada permitiu confirmar o estado sem alterar configurações Git.

## Fluxo atual observado

1. backend/seed.py declara o bloco quiz com enunciado, alternativas, correct_index e explanation.
2. GET /api/nodes/{node_id} chama services/nodes.py:get_node. Para estudantes, _student_block remove answer, correct_index e explanation em blocos avaliativos.
3. frontend/src/components/blocks/BlockRendererParts.tsx:QuizBlock continua lendo correct_index, corrige no navegador, grava selected/correct pelo callback de progresso, apresenta explanation e permite nova tentativa. Há incompatibilidade entre a projeção segura da API e o renderer atual.
4. POST /api/progress recebe status/data genéricos e services/progress.py:set_progress persiste esses valores. O status enviado pelo cliente não é correção autoritativa.
5. POST /api/submissions/submit usa submit_answer; o serviço verifica a capacidade submission do tipo. O tipo quiz não está no conjunto SUBMITTABLE de backend/seed.py. Não foi identificado fluxo implementado de submissão e correção automática para quiz.
6. A correção manual de submissões usa a permissão submissions.grade, mas não substitui uma API de quiz com correção automática.

Referências mais específicas e a proposta de fluxo estão em ESPECIFICACAO_QUIZZES.md e CONTRATOS_API_QUIZZES.md.

## Contratos documentados

- Quiz público: somente enunciado, formato, alternativas, ordem, identificador e revisão.
- Tentativa: revisão, contexto curricular, resposta tipada e chave idempotente; identidade vem da sessão.
- Resultado: correção pelo servidor e revelação condicionada à política, sem concluir automaticamente a unidade.
- Histórico: escopado ao estudante e preservado por revisão.
- Correção administrativa: dados do gabarito em projeção protegida e separada.

O vínculo do contrato intermediário permanece explícito: QuizBlock.answer_key_ref deve apontar para AnswerKeyBlock.ref, e AnswerKeyBlock.question_ref deve retornar ao quiz. student_quiz_view continua sendo a projeção segura existente. Nenhum gabarito foi transformado em theory_text.

## Política recomendada

[PROPOSTA] Permitir um limite configurável por revisão e liberar correção detalhada, resposta correta e explicação após a última tentativa disponível. Antes disso, confirmar o registro sem expor acerto, chave ou explicação. Preservar todas as tentativas e as revisões usadas.

Permanecem decisões de produto: limite padrão, reinício, exceções para quizzes formativos, revelação de explicações, correção de respostas abertas, política de histórico e relação entre quiz e conclusão curricular. O limite de duas tentativas usado nos fixtures é apenas dado de teste.

## Testes

Arquivo novo: backend/unit_tests/test_quiz_api_contracts.py, com 17 testes. O simulador exerce:

- projeção pública sem gabarito e preservação da ordem das opções;
- rejeição de campos privados no schema público e de identidade/resultado no envio;
- correção determinística usando AnswerKeyBlock;
- rejeição de alternativa inexistente e formato sem avaliador;
- idempotência para repetição idêntica e conflito para corpo divergente;
- revelação conforme política e limite;
- revisão obsoleta sem apagar histórico;
- isolamento do histórico por estudante;
- autorização administrativa separada;
- vínculo question_ref sem associação por proximidade;
- autenticação e bloqueio de acesso.

O módulo não importa FastAPI routes, services de submissão/progresso, configuração de aplicação ou cliente MongoDB. Os testes são de contrato e não são testes de integração da API.

## Verificações executadas

Ambiente: Python 3.13.15, Pydantic 2.13.5, pytest 9.1.1.

- pytest unit_tests/test_quiz_api_contracts.py unit_tests/test_curriculum_contract.py -q: 48 passed.
- Ruff check no teste novo: aprovado.
- Ruff format --check no teste novo: aprovado.
- mypy no teste novo: aprovado, sem issues.
- compileall no teste novo: aprovado.

Uma primeira coleta revelou que QuizOption não é reexportado pelo pacote curriculum_contract; o teste passou a importá-lo do módulo curriculum_contract.models, que é sua localização real. O mypy também apontou que correct_option_ref é opcional no schema intermediário; o fixture agora valida explicitamente sua presença antes de construir a revelação. Ambas as correções ficaram limitadas ao teste novo.

Não foram executados testes de integração que possam acessar banco, nem validações gerais da aplicação que importem a configuração de produção.

## Arquivos criados

- backend/unit_tests/test_quiz_api_contracts.py
- docs/migracao/ESPECIFICACAO_QUIZZES.md
- docs/migracao/CONTRATOS_API_QUIZZES.md
- docs/migracao/RELATORIO_ETAPA_13B.md

## Limitações e próximos passos

A simulação não garante autenticação, autorização, idempotência concorrente, persistência append-only, rate limiting ou ocultação de dados em um endpoint real. Essas garantias exigem implementação e testes de integração em etapa futura.

Antes da implementação, é necessário aprovar as políticas de tentativas, revelação, histórico, conclusão e correção de formatos além de multiple_choice. A futura implementação deve alterar backend e renderer em etapas separadas, com testes de privacidade e concorrência. Esta entrega não aprova nem implementa nenhuma dessas mudanças.

## Estado final pretendido

Somente quatro arquivos novos da Etapa 13B; nenhum arquivo rastreado modificado, nenhum item preexistente removido, nenhum arquivo staged e nenhum commit.