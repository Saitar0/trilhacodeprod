# Contratos implementados para a API de quizzes — Etapa 13C.1

Este documento atualiza os exemplos conceituais registrados na Etapa 13B. A API descrita aqui está implementada no backend; a adaptação do renderer continua pendente. Os exemplos abaixo não incluem dados da chave antes da condição de revelação.

## Leitura pública do quiz

`GET /api/quizzes/{quiz_id}` exige sessão autenticada e acesso ao tópico. Retorna a versão ativa, enunciado, ordem, alternativas e estado do próprio usuário.

~~~json
{
  "quiz_id": "65a000000000000000000001",
  "version_id": "65a000000000000000000010",
  "curriculum_ref": "f1-question-example",
  "title": "Quiz de exemplo",
  "questions": [
    {
      "question_id": "65a000000000000000000002",
      "order": 0,
      "prompt": "Qual alternativa está correta?",
      "options": [
        {"option_id": "option-1", "text": "Alternativa A"},
        {"option_id": "option-2", "text": "Alternativa B"}
      ]
    }
  ],
  "attempts_used": 0,
  "attempts_remaining": 3,
  "passed": false,
  "best_score_percent": null,
  "review_available": false
}
~~~

O payload público não contém resposta correta, explicação, hash de conteúdo ou dados administrativos. Os IDs de alternativas são estáveis dentro do snapshot e a ordem é preservada.

## Submissão

`POST /api/quizzes/{quiz_id}/attempts` exige sessão e o cabeçalho `Idempotency-Key`. O servidor identifica o usuário pela sessão e não aceita campos extras no corpo.

~~~http
Idempotency-Key: 4d2b9c87-1668-41a4-9f35-0b1fc30dcaa1
Content-Type: application/json
~~~

~~~json
{
  "version_id": "65a000000000000000000010",
  "answers": [
    {"question_id": "65a000000000000000000002", "option_id": "option-1"}
  ]
}
~~~

`user_id`, `score`, `passed`, `correct_answers` e `attempt_number` são recusados como campos adicionais. Questões desconhecidas, alternativas externas e respostas duplicadas são rejeitadas. Questões omitidas contam como incorretas, mas a submissão continua válida e consome uma tentativa.

## Resultado da tentativa

O servidor corrige e retorna a pontuação calculada, aprovação, número de tentativa, tentativas restantes, melhor nota e indicação de disponibilidade de revisão. A comparação com 70% não arredonda antes do cálculo. Nenhuma resposta correta ou explicação acompanha o resultado.

~~~json
{
  "attempt_id": "65a000000000000000000020",
  "quiz_id": "65a000000000000000000001",
  "version_id": "65a000000000000000000010",
  "attempt_number": 1,
  "total_questions": 1,
  "score_percent": 100.0,
  "passed": true,
  "attempts_used": 1,
  "attempts_remaining": 2,
  "best_score_percent": 100.0,
  "review_available": false,
  "submitted_at": "2026-10-27T12:00:00Z"
}
~~~

A aprovação antecipada não encerra as tentativas nem libera revisão. Após a terceira tentativa válida, `review_available` passa a ser verdadeiro; o resultado ainda não incorpora a chave.

## Histórico

`GET /api/quizzes/{quiz_id}/attempts` retorna apenas tentativas do usuário autenticado, paginadas por `limit` e `skip`. Preserva versão, pontuação, aprovação, data e número da tentativa. Não retorna respostas submetidas nem gabaritos.

## Revisão após esgotamento

`GET /api/quizzes/{quiz_id}/versions/{version_id}/review` confere no servidor se o próprio usuário utilizou as três tentativas da versão solicitada. Antes disso, retorna 403. Depois disso, retorna alternativas corretas e explicações daquela versão imutável.

Revisões antigas permanecem disponíveis apenas para usuários que esgotaram as tentativas daquela versão. Uma versão nova inicia contagem própria.

## Publicação administrativa de uma versão

`POST /api/admin/quizzes/{quiz_id}/versions` exige a permissão existente `content.publish`. O serviço valida blocos `quiz` publicados e cria ou reutiliza um snapshot imutável. Aceita o formato legado (`question`, alternativas textuais, `correct_index`) e a projeção tipada (`prompt`, alternativas com referências e `AnswerKeyBlock` associado); a referência do gabarito precisa apontar para a questão e para uma das alternativas. A resposta contém somente o identificador da versão, título, quantidade de questões e data de criação; não há endpoint administrativo de leitura do gabarito nesta etapa.

As alterações em conteúdo-fonte só entram em vigor para os alunos depois de publicar um novo snapshot. A publicação exige que cada questão tenha enunciado, ao menos duas alternativas e um índice inteiro de resposta correta válido. Pesos explícitos são rejeitados porque o modelo atual não os valida.

## Persistência e idempotência

- `quiz_versions` armazena snapshots, gabaritos e explicações privados; seu identificador é um `ObjectId` e o hash do conteúdo é privado.
- `quiz_catalog` aponta para a versão ativa do quiz.
- `quiz_progress` é um agregado por usuário, quiz e versão. Preserva até três registros imutáveis de tentativa e a projeção derivada da melhor nota.
- O índice único do agregado e a atualização condicional atômica impedem números duplicados e mais de três tentativas concorrentes.
- A chave de idempotência é armazenada como hash dentro do agregado. O mesmo corpo retorna exatamente o resultado persistido; outro corpo com a mesma chave gera conflito.
- O backend não grava conclusão no endpoint genérico de progresso.

Os códigos HTTP continuam no envelope de erro comum da API (`unauthorized`, `forbidden`, `not_found`, `conflict` e `validation_error`). Não são expostos detalhes de correção em erros ou logs de requisição.

## Limitações nesta etapa

- O renderer atual ainda usa o fluxo antigo de correção local e não consome estes endpoints.
- O avaliador implementado aceita somente múltipla escolha de resposta única.
- Não existe endpoint de administração para inspecionar chaves ou gerir versões.
- Tentativas e resultados não estão integrados à conclusão curricular.
- Os testes MongoDB usam apenas um banco descartável local; não comprovam configuração de replica set ou comportamento de produção.
