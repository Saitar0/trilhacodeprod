# Relatório — Etapa 13C.2

## Resultado

O renderer recebeu um fluxo alternativo que usa a API autenticada de quizzes. O fluxo está **desativado por padrão** e não foi ativado em produção. Quando habilitado em uma build isolada, ele substitui a correção local do quiz por uma sessão controlada pelo servidor. Em falhas da API, não há fallback para correção no navegador.

Esta entrega é tecnicamente concluída para os testes executados, com a limitação de não haver teste ponta a ponta de navegador conectado ao backend nesta rodada. A homologação operacional continua pendente.

## Arquivos desta etapa

- Modificados: `frontend/.env.example`, `frontend/src/vite-env.d.ts`, `frontend/src/components/blocks/BlockProps.ts`, `frontend/src/components/blocks/BlockRenderer.tsx`, `frontend/src/components/student/NodeReader.tsx`.
- Criados: `frontend/src/components/blocks/QuizApiSession.tsx`, `frontend/src/lib/quizApi.ts`, `frontend/src/lib/quizFeature.ts` e os três arquivos de teste correspondentes.
- Documentação: este relatório e `INTEGRACAO_FRONTEND_QUIZZES.md`.

As modificações locais de backend e migração preexistentes foram preservadas. Nenhum arquivo curricular, JSON legado, contrato intermediário, backend de produção ou renderer não relacionado foi alterado nesta etapa.

## Integração

O `NodeReader` identifica o primeiro bloco `quiz` de um tópico e monta uma sessão API para o nó inteiro, usando o ID do nó como `quiz_id`, conforme a API existente. Os blocos `quiz` irmãos são ocultados nessa modalidade para não apresentar duplicações do quiz que o backend publica como uma versão por nó. Outros tipos de bloco continuam no renderer existente.

O `BlockRenderer` aceita uma substituição de conteúdo específica. Para o quiz API, o bloco fornecido ao shell visual recebe `data: {}`; o renderer legado de quiz não lê nem corrige o gabarito. O callback do endpoint genérico de progresso não é passado à sessão API. A integração não grava aprovação curricular nem altera regras de desbloqueio.

O cliente usa o Axios existente, com `withCredentials: true` e o mecanismo atual de renovação de sessão. As rotas usadas são:

- `GET /api/quizzes/{quiz_id}`
- `POST /api/quizzes/{quiz_id}/attempts`, com `Idempotency-Key`
- `GET /api/quizzes/{quiz_id}/attempts`
- `GET /api/quizzes/{quiz_id}/versions/{version_id}/review`

Os formatos seguem `backend/schemas/quizzes.py` e `backend/routes_quizzes.py`; não foram inventados endpoints ou campos.

## Experiência e segurança no cliente

- Perguntas e opções vêm do payload público, sem chave de resposta.
- O cliente envia apenas `version_id` e pares `question_id`/`option_id`; nota e aprovação vêm da resposta do servidor.
- Aprovação não encerra tentativas restantes. Pontuação, melhor nota e tentativas disponíveis são exibidas conforme a API.
- A revisão só é solicitada se `review_available` vier habilitado pela API. O servidor continua sendo a autoridade final e protege a rota de revisão.
- O histórico usa somente a resposta tipada de tentativas; não recebe respostas corretas nem explicações.
- Cada nova intenção ganha uma chave de idempotência. Respostas e chave ficam em `sessionStorage`, com escopo por usuário e quiz, e são reutilizadas no retry da mesma intenção. Um novo envio deliberado recebe outra chave. A chave não é um controle de segurança e a API permanece responsável pela idempotência.
- `sessionStorage` preserva a intenção em retries e recarga na mesma aba, mas não é armazenamento durável após o encerramento da aba; se o armazenamento estiver indisponível, o retry só pode ser mantido em memória enquanto a página permanecer aberta.
- Cliques duplicados são bloqueados durante o envio. O limite real continua sendo aplicado no backend.
- Os erros 400, 401, 403, 404, 409, 422, 429 e 5xx são convertidos em mensagens sem detalhes internos. Timeout e falha de rede mantêm a intenção para retry. Em 429, o cliente interpreta `Retry-After` em segundos ou data HTTP e bloqueia a ação durante a espera indicada.
- Formulários usam `fieldset`/`legend`, rótulos de rádio, foco visível e regiões `status`/`alert`.

## Feature flag e rollback

`VITE_QUIZ_API_ENABLED` é uma configuração de build do Vite, não um toggle em tempo de execução. Só o valor literal `true` ativa o fluxo. O padrão e o valor em `frontend/.env.example` são `false`. Nenhuma configuração de produção foi alterada.

Para testar, configure a flag somente no ambiente/build isolado que tenha a API de quizzes acessível e conteúdo publicado. Para rollback, remova a variável ou defina `false` e gere/republique a build aprovada anterior. Não é preciso apagar tentativas do servidor. Uma intenção pendente pode permanecer no navegador; se o fluxo for reativado, ela deve continuar usando a mesma chave. Alternar para o renderer legado enquanto houver submissões pendentes pode deixar o aluno sem retomada visível da intenção, embora o resultado persistido continue no backend.

## Verificações executadas

Comandos e resultados:

- `npm test -- --reporter=dot src/components/blocks/QuizApiSession.test.tsx src/lib/quizApi.test.ts src/lib/quizFeature.test.ts` — 34 testes aprovados.
- `npm test -- --reporter=dot` — 45 testes aprovados em 7 arquivos.
- `npm run typecheck` — aprovado.
- `npm run lint` — aprovado.
- `npm run build` — aprovado.
- `py -3.13 -m pytest tests/test_quizzes.py -q --tb=short` (diretório `backend/`) — 26 testes aprovados em 15,13 s.
- `git diff --check` — aprovado.

Para a regressão backend, `backend/tests/conftest.py` e `backend/test_support/mongo_target.py` foram inspecionados antes da execução. `MONGO_URL_TEST` não estava configurada; o fixture usou o MongoDB local de loopback, forçou `directConnection=true`, criou um nome aleatório no padrão `test_<32 hex>` e removeu somente essa base descartável ao final. Nenhum banco remoto ou de produção foi usado.

Não foi encontrado um spec E2E de Playwright para o fluxo API do quiz. Não foi executado teste de navegador contra backend real, teste de ativação em ambiente isolado, nem fluxo frontend + API + MongoDB em uma única execução. Os testes Vitest mockam a fronteira de rede e não comprovam operação de produção. Não há script de formatação separado no `package.json`; lint, TypeScript e build passaram.

`npm ci --ignore-scripts --no-audit --no-fund` foi necessário porque as dependências locais do frontend não estavam instaladas. O lockfile permaneceu inalterado. Foram observados avisos de depreciação de dependências, sem mudanças de versões.

## Pendências e riscos

1. Executar um E2E controlado com frontend e backend, conteúdo de quiz publicado e banco descartável antes de qualquer ativação operacional.
2. Confirmar com produto se a pontuação agregada imediata é aceitável: sem revelar item a item, uma nota pode permitir inferir respostas por repetição. O backend já devolve a pontuação segundo a política aprovada.
3. Validar o agrupamento de todos os blocos `quiz` de um nó em uma única versão publicada para cada conteúdo que vier a ser ativado.
4. Resolver a integração de aprovação com pré-requisitos curriculares na Etapa 13C.3; esta implementação não usa o endpoint genérico de progresso como evidência de aprovação.
5. A ativação depende de configuração explícita de build. O valor desativado no exemplo não substitui a conferência das variáveis do pipeline de cada ambiente.

## Estado final

Nenhuma ativação real, importação curricular, alteração do JSON ou commit foi realizada. As alterações locais preexistentes foram mantidas e o índice Git permaneceu vazio.
