# Integração do renderer com a API de quizzes

## Escopo e estado

Este documento descreve a integração frontend da Etapa 13C.2. O caminho novo é opt-in em uma build isolada e permanece desligado por padrão. Não houve ativação em produção, importação curricular ou alteração do progresso curricular.

## Fluxo do aluno

1. `NodeReader` carrega o nó e seus blocos pelo fluxo atual.
2. Com `VITE_QUIZ_API_ENABLED` diferente do literal `true`, o renderer legado permanece em uso.
3. Com a flag habilitada, o primeiro bloco `quiz` ancora uma sessão API para o nó; os blocos `quiz` adicionais daquele mesmo nó não são apresentados novamente. A API usa `node.id` como `quiz_id`.
4. A sessão consulta `GET /api/quizzes/{quiz_id}` e `GET /api/quizzes/{quiz_id}/attempts`.
5. O aluno responde às alternativas fornecidas pela API. A interface não contém correção local.
6. Ao enviar, a interface envia `{version_id, answers:[{question_id, option_id}]}` e o cabeçalho `Idempotency-Key` para `POST /api/quizzes/{quiz_id}/attempts`.
7. A interface mostra resultado, aprovação, melhor nota e tentativas conforme a resposta do backend. Uma aprovação anterior não impede o uso das tentativas restantes.
8. O renderer consulta revisão somente quando `review_available` fornecido pelo backend é verdadeiro. A revisão contém as respostas corretas e explicações, e continua protegida pela autorização no servidor.

## Contratos realmente utilizados

As definições frontend estão em `frontend/src/lib/quizApi.ts`; as rotas e schemas do backend correspondentes estão em `backend/routes_quizzes.py` e `backend/schemas/quizzes.py`.

| Ação | Rota | Uso |
|---|---|---|
| Quiz público | `GET /api/quizzes/{quiz_id}` | Versão, título, perguntas, opções, tentativas, melhor nota, aprovação e `review_available`; sem chave ou explicação. |
| Enviar tentativa | `POST /api/quizzes/{quiz_id}/attempts` | `version_id`, respostas por ID e cabeçalho de idempotência; nota nunca vem do cliente. |
| Histórico | `GET /api/quizzes/{quiz_id}/attempts` | Resultados e datas das tentativas autenticadas do próprio usuário. |
| Revisão | `GET /api/quizzes/{quiz_id}/versions/{version_id}/review` | Opções marcadas como corretas e explicações, somente após autorização do servidor. |

O cliente usa a instância Axios compartilhada (`frontend/src/lib/api.ts`), que envia cookies (`withCredentials`) e já possui o fluxo de renovação de sessão para respostas 401. O frontend não cria publicação de versões nem fornece chave de resposta.

## Política apresentada

- Três tentativas por usuário, quiz e versão.
- Aprovação calculada no servidor a partir de 70%, sem decisão local.
- Nota recebida imediatamente após cada envio; melhor nota exibida conforme o servidor.
- Tentativas restantes permanecem disponíveis mesmo após aprovação.
- Histórico de tentativas consultado na API.
- Gabarito e explicações só aparecem quando a API autoriza a revisão após a terceira tentativa válida.

O servidor pode autorizar revisão ao carregar um quiz que já esgotou tentativas; por isso a condição é lida da API e nunca inferida somente do estado local.

## Retry e erros

A chave identifica uma intenção, não uma tentativa de rede. A chave e as respostas submetidas ficam em `sessionStorage` por usuário e quiz. Timeout, erro de rede, 401 após o fluxo compartilhado de renovação, 429 e 5xx permitem reenviar a mesma intenção com a mesma chave. Uma nova ação deliberada cria uma nova chave. Se a versão mudar, respostas antigas não são enviadas à nova versão sem confirmação explícita do aluno.

Para 429, `Retry-After` é respeitado como segundos ou data HTTP. Mensagens exibidas não incluem corpos ou detalhes internos do servidor. 400/422 pedem revisão explícita das respostas; 403/404 informam indisponibilidade/autorização; 409 solicita atualização do quiz. Timeout é configurado para 20 segundos.

Como a chave pendente fica em `sessionStorage`, o retry é preservado durante a sessão/aba e recargas nela. Fechar a aba pode remover a chave; essa limitação deve ser considerada antes da ativação operacional. Uma confirmação de submissão ainda é determinada pelo histórico e pelo servidor, nunca por uma nota local.

## Progresso curricular

A sessão API não chama o callback de progresso por bloco e não envia `score`, `passed` ou dados equivalentes ao endpoint genérico de progresso. Os recursos já existentes do `NodeReader` para visita/leitura e para a ação manual “Marcar como concluído” continuam fora desta alteração. Portanto, a aprovação do quiz ainda não é integrada a pré-requisitos nem substitui o progresso de leitura. Isso fica para a Etapa 13C.3.

## Flag e rollback

`VITE_QUIZ_API_ENABLED` é definida na compilação do Vite; não é uma flag dinâmica remota. O código só ativa para `"true"`; ausência, `false` ou qualquer outro valor mantém o renderer legado. `frontend/.env.example` registra `false`.

Para teste isolado, configurar `true` somente na build e ambiente controlados que apontem para uma API de teste com quiz publicado. Antes de liberar tráfego real, conferir que a configuração do pipeline de produção continua ausente ou falsa. Para rollback, reconstruir/publicar com a variável removida ou falsa. Não apagar tentativas backend. Se houver intenção pendente no navegador, preservar a possibilidade de reativar o fluxo para reenviá-la com a mesma chave; o renderer legado não exibe essa intenção.

## Verificações e limites

Foram aprovados 45 testes frontend (7 arquivos), incluindo contratos de rota, ausência de gabarito no payload público, fluxo de tentativas, revisão, idempotência, retry, 429, erros de sessão e autorização, troca de versão e flag desligada. Typecheck, lint e build frontend passaram.

A regressão `backend/tests/test_quizzes.py` passou com 26 testes em MongoDB local descartável. Não foi executado E2E de navegador com API real: o repositório não contém um spec Playwright específico para esta integração. Os testes frontend mockam a rede; o teste backend valida a API separadamente. Antes de ativar, falta uma execução E2E conjunta no ambiente isolado com publicação de versão e banco descartável.
