# Implementação do backend de quizzes — Etapa 13C.1

## Escopo implementado

A API agora publica snapshots imutáveis de quizzes, entrega uma visão pública sem gabarito, corrige tentativas no servidor, preserva histórico por usuário e versão e libera revisão somente após três tentativas válidas. A aprovação é calculada a partir de pelo menos 70% de acertos. A maior pontuação permanece como resultado de melhor nota.

Esta implementação não altera o renderer, o JSON legado, a árvore curricular, o importador ou o endpoint genérico de progresso. O aluno ainda verá a incompatibilidade do renderer até a Etapa 13C.2; portanto, esta etapa entrega o backend e o contrato HTTP, mas não ativa o novo fluxo no navegador.

## Arquivos

| Arquivo | Responsabilidade |
|---|---|
| `backend/schemas/quizzes.py` | Modelos estritos de request e resposta pública, tentativa, histórico, revisão e publicação. Campos desconhecidos no envio são recusados. |
| `backend/services/quizzes.py` | Publicação de snapshots, validação de fonte, correção, idempotência, reserva concorrente, histórico e revisão autorizada. |
| `backend/routes_quizzes.py` | Endpoints autenticados de leitura, submissão, histórico, revisão e publicação administrativa. |
| `backend/migrations/0003_quiz_attempts.py` | Cria os índices necessários ao catálogo de versões e ao agregado de progresso. |
| `backend/migrations/__init__.py` | Registra a migração 0003 como versão esperada do schema. |
| `backend/indexes.py` | Define índices e os inclui na pré-verificação operacional. |
| `backend/server.py` | Registra o roteador, exige a migração 0003 para `/ready` e permite o cabeçalho `Idempotency-Key` no CORS. |
| `backend/tests/test_quizzes.py` | Testes HTTP com FastAPI e banco MongoDB local descartável. |
| `backend/unit_tests/test_quiz_grading.py` | Testes unitários do avaliador determinístico. |
| `backend/tests/test_integrity_concurrency.py` | Atualiza a contagem esperada de índices. |
| `ops/g2/preflight-manifest-v1.json` | Acrescenta as verificações dos índices únicos necessários para o fluxo. |

## Endpoints

- `GET /api/quizzes/{quiz_id}`: requer autenticação, visibilidade e acesso curricular; retorna somente enunciados, alternativas e estado resumido do próprio usuário.
- `POST /api/quizzes/{quiz_id}/attempts`: requer sessão e `Idempotency-Key`; aceita `version_id` e respostas `{question_id, option_id}`. A identidade do usuário vem da sessão.
- `GET /api/quizzes/{quiz_id}/attempts`: retorna o histórico do usuário autenticado, sem respostas submetidas ou gabaritos.
- `GET /api/quizzes/{quiz_id}/versions/{version_id}/review`: libera alternativa correta e explicação apenas quando o servidor confirma três tentativas válidas daquela versão para aquele usuário.
- `POST /api/admin/quizzes/{quiz_id}/versions`: exige a permissão existente `content.publish`, valida os blocos publicados e cria ou reusa um snapshot imutável.

Os endpoints de leitura, tentativa, histórico, revisão e publicação usam o limitador Mongo-backed compartilhado da plataforma. Os limites padrão por usuário autenticado, por janela móvel de 60 segundos, são: leitura 120, tentativas 10, histórico 60, revisão 30 e publicação 10. Cada endpoint retorna HTTP 429 com `Retry-After` e código `rate_limited` quando o bucket está esgotado. Os valores podem ser configurados por `QUIZ_READ_LIMIT_PER_MINUTE`, `QUIZ_ATTEMPT_LIMIT_PER_MINUTE`, `QUIZ_HISTORY_LIMIT_PER_MINUTE`, `QUIZ_REVIEW_LIMIT_PER_MINUTE` e `QUIZ_PUBLISH_LIMIT_PER_MINUTE`. Retries idempotentes já concluídos são respondidos antes de consumir o limite de tentativas.

Não foi criado endpoint administrativo de leitura da chave. O endpoint de publicação retorna apenas o ID da versão, título, quantidade de questões e data.

## Persistência

`quiz_versions` armazena snapshot com ID estável do quiz, ID da versão, referência curricular disponível, origem no nó/bloco, título, perguntas e alternativas ordenadas, resposta correta como `correct_option_id`, explicação privada, hash SHA-256, estado `published` e metadados de criação. A chave fica somente nesse documento privado.

`quiz_catalog` aponta o quiz para a versão ativa. `quiz_progress` é um agregado por usuário/quiz/versão. Contém o contador, melhor resultado e uma lista de no máximo três tentativas imutáveis, cada uma com ID, respostas submetidas, hashes idempotentes, correção, nota e data. Não existe rota do aluno para editar ou excluir esse histórico.

O índice único `(quiz_id, content_hash)` deduplica a publicação do mesmo snapshot; o índice único `(user_id, quiz_id, version_id)` garante um agregado por escopo. A atualização condicional do agregado é atômica no MongoDB e reserva `attempt_number` junto com a tentativa. Por isso, a submissão não depende de transação entre coleções. Se a publicação gravar o snapshot mas falhar antes de atualizar o catálogo, o snapshot fica inativo; repetir a publicação pode apontar o catálogo para o mesmo snapshot. O histórico é paginado por agregação no MongoDB, sem truncar após uma quantidade fixa de versões.

A versão é identificada pelo snapshot de conteúdo: republicar conteúdo idêntico reusa a mesma versão e sua contagem de tentativas; conteúdo avaliativo diferente gera outra versão e limite próprio.

## Correção, precisão e limites

O avaliador suporta múltipla escolha com uma resposta correta. A publicação aceita o formato legado (`question`/`options`/`correct_index`) e a projeção tipada do contrato intermediário (`prompt`, alternativas identificadas e `AnswerKeyBlock` associado). No formato tipado, referências da questão, do gabarito e da alternativa correta são verificadas; explicações e proveniência seguem no snapshot privado. Isso foi exercitado por fixtures tipadas sem importar a árvore curricular. Quiz sem questão avaliável, enunciado, alternativas ou gabarito válido, e qualquer peso explícito são rejeitados; pesos não são ignorados porque o modelo atual não os valida.

Respostas omitidas contam como incorretas; questões desconhecidas, alternativas externas e respostas duplicadas são recusadas e não consomem tentativa. O denominador é o total de questões da versão. O servidor compara `correct_answers * 100 >= 70 * total_questions`; só a apresentação arredonda para duas casas.

## Concorrência e idempotência

O agregado é criado por upsert com índice único. Cada submissão lê `attempt_count` e atualiza somente se o contador ainda corresponder e a chave idempotente ainda não existir no histórico. A operação atômica incrementa o contador e acrescenta a tentativa. Em corrida, quem perde relê o agregado: mesma chave e mesmo corpo recebem o resultado já persistido; mesma chave e outro corpo recebem 409. Chaves diferentes competem por posições distintas até três; a quarta submissão recebe 409.

A chave bruta não é persistida; somente seu SHA-256. O hash do corpo vincula idempotência à versão e às respostas. O retorno inicial também é montado a partir do documento persistido para que uma repetição devolva os mesmos valores e precisão de timestamp.

Uma falha antes da atualização atômica não reserva tentativa. Se a atualização for persistida mas a resposta HTTP se perder, repetir a mesma chave recupera o resultado. Se a disponibilidade do banco falhar durante a gravação, o cliente deve repetir a chave original; uma nova chave poderia representar nova tentativa caso a primeira gravação tenha sido confirmada sem resposta.

## Segurança

As rotas usam `current_user`; leitura, tentativa e revisão passam pelas verificações de visibilidade e pré-requisitos existentes. A publicação usa `require("content.publish")`. Consultas de progresso sempre incluem o usuário da sessão. A revisão verifica elegibilidade no servidor em cada chamada.

Schemas de saída são allowlists. O quiz público e o histórico não incluem gabarito, explicações, respostas submetidas ou hash. O resultado retorna nota, aprovação e contadores aprovados, mas não informa contagem de acertos nem quais respostas individuais estavam corretas. Erros de validação são genéricos e o middleware registra rota, status e usuário, não corpo nem conteúdo da correção. O endpoint genérico de progresso permanece inalterado e não participa da correção ou aprovação. A pontuação agregada pode permitir inferência em um quiz de uma questão; a divulgação imediata da nota foi mantida conforme a política aprovada.

## Compatibilidade e limitações

- A fonte atual dos quizzes de produção continua sendo `content_blocks` com `question`, `options`, `correct_index` e `explanation`.
- A fronteira de publicação também aceita a projeção tipada descrita acima, mas ainda não existe conversor entre os 3.431 blocos curriculares e `content_blocks`.
- A publicação administrativa é explícita; nenhum conteúdo curricular foi importado ou convertido.
- Os IDs de questão usam o ID persistente do bloco. `curriculum_ref` só é preenchido quando `node.meta.import_ref` existe.
- O renderer atual continua esperando correção no navegador e não foi alterado.
- Não há integração do resultado com conclusão curricular.
- A visibilidade e os bloqueios de pré-requisito reutilizam `assert_visible`/`assert_unlocked`. Nota, aprovação, contador e revisão não dependem de `POST /api/progress`; porém, a conclusão de pré-requisitos não-quiz ainda vem do progresso legado, cujo status pode ser informado pelo cliente. Essa dependência para desbloqueio exige endurecimento separado.
- Não há avaliadores para resposta aberta, ordenação ou código.
- O banco de teste local é standalone; testes aprovados não comprovam uma implantação MongoDB com replica set nem sua política de backup/restore.
- Não foi conectado a MongoDB de produção nem executado o comando de migração fora do harness descartável dos testes.

## Próxima etapa

A Etapa 13C.2 deve adaptar o renderer para consumir o quiz público, enviar `Idempotency-Key`, mostrar o resultado do servidor e chamar a revisão apenas quando `review_available` indicar elegibilidade. Não deve transportar gabaritos para o navegador antes disso. A integração com progresso curricular requer decisão e autorização separadas.
