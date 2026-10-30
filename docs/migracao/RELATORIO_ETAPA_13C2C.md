# Relatório — Etapa 13C.2C

Data: 2026-10-28

Escopo: recuperação autoritativa de tentativas de quiz e investigação focada da instabilidade E2E `student-progress`. Não houve ativação operacional, importação curricular ou alteração de progresso global.

## Resultado

**Concluída com ressalvas.** O servidor agora permite consultar uma tentativa persistida por chave de idempotência e a tentativa mais recente por quiz/versão quando a chave local se perdeu. As consultas são autenticadas, escopadas por usuário, quiz e versão, somente de leitura e não consomem tentativas. O renderer reconcilia o estado com a API, não cria novo envio automaticamente e mantém a proteção do gabarito.

O servidor não mantém uma reserva persistente separada. Como a tentativa e seu resultado são escritos juntos por uma atualização atômica, não existe estado durável `pending`; uma consulta sem resultado retorna `unknown` com `may_still_be_processing: true`. Isso não afirma que a intenção falhou. Sem chave e sem tentativa persistida, não é possível provar que uma intenção perdida chegou ao servidor.

## Alterações desta etapa

- `backend/schemas/quizzes.py`: contratos de entrada e saída da recuperação.
- `backend/services/quizzes.py`: consulta por hash da chave ou último resultado, sem mutação de tentativas.
- `backend/routes_quizzes.py`: endpoint autenticado `POST /api/quizzes/{quiz_id}/recovery`.
- `backend/tests/test_quizzes.py`: testes de confirmação, desconhecido, consulta sem consumo, isolamento por usuário e versão.
- `frontend/src/lib/quizApi.ts`: tipo e cliente do endpoint.
- `frontend/src/components/blocks/QuizApiSession.tsx`: reconciliação automática e consulta manual do último resultado; sem submissão automática de nova tentativa.
- `frontend/src/components/blocks/QuizApiSession.test.tsx`: testes de estados de recuperação.
- `frontend/e2e/quiz-api-real.spec.ts`: cobertura de resultado persistido com armazenamento perdido e verificação de que não há POST de tentativa durante a recuperação.
- `frontend/e2e/quiz-api-restart-history.spec.ts`: recuperação pela chave após reinício e verificação de isolamento entre versões.
- `frontend/e2e/student-progress.spec.ts`: lida com o estado real do aluno seedado, iniciando a trilha ou retomando a atividade persistida e limpando somente o tópico do teste antes de marcá-lo novamente.
- `docs/migracao/RECUPERACAO_SUBMISSOES_QUIZ.md`: contrato e limites da recuperação.

`VITE_QUIZ_API_ENABLED` não foi alterada e permanece falsa quando ausente por padrão no helper de feature flag. Não foram alterados o JSON curricular, o contrato intermediário, as árvores curriculares, o frontend genérico de progresso ou as regras de desbloqueio.

## Contrato e estados

`POST /api/quizzes/{quiz_id}/recovery` recebe `version_id` e opcionalmente `idempotency_key`.

- `confirmed`: a chave corresponde a uma tentativa persistida; retorna o resultado dessa tentativa.
- `latest_confirmed`: sem chave, retorna a tentativa concluída mais recente da versão; não a associa a uma intenção perdida.
- `unknown`: não há correspondência visível no momento; `may_still_be_processing` permanece verdadeiro.

O serviço valida a versão do quiz, usa o usuário autenticado, consulta somente o documento de progresso daquele usuário, aplica o limite existente de consultas e nunca retorna respostas corretas ou explicações. Tentativas persistidas continuam contendo o hash da chave, não a chave original.

## Instabilidade `student-progress`

A causa reproduzível era estado persistente da conta de teste: após uma execução, o endpoint de progresso preservava `last_node_id`, e a página mostrava `track-resume-button` em vez de `track-start-button`. O teste exigia apenas o botão de início. A correção mínima aceita ambos os estados e reseta o tópico de teste quando já aparece como concluído antes de repetir a ação. Não foram adicionados retries globais nem aumentados timeouts.

O teste passou em duas execuções da suíte E2E geral usando o mesmo banco descartável. Não foi identificada dependência de ordem além do estado persistente seedado; a cobertura agora exercita explicitamente esse estado de retomada.

## Testes e ambiente

| Verificação | Resultado |
|---|---|
| `backend/tests/test_quizzes.py` | 30 aprovados em MongoDB descartável explícito |
| Testes frontend Vitest | 50 aprovados em 7 arquivos |
| `npm run typecheck` | aprovado |
| `npm run lint` | aprovado |
| `ruff check` nos módulos e teste de quiz | aprovado |
| `ruff format --check` nos arquivos backend pertinentes | aprovado |
| Mypy focado nos schemas, rotas e serviço de quiz | aprovado |
| Compilação Python dos arquivos backend pertinentes | aprovada |
| `quiz-api-real.spec.ts` | 9/9 aprovados em Chromium, com frontend e API reais |
| `quiz-api-restart-history.spec.ts` | 1/1 aprovado após reinício da API e mantendo o MongoDB descartável |
| Suíte E2E geral | duas execuções: cada uma com 12 aprovados, 3 ignorados e zero falhas; `student-progress` passou nas duas |

O MongoDB era 9.0.2, iniciado para esta execução em `127.0.0.1:27251`, conexão direta, topologia standalone e banco exclusivo `tc13c2c_e2e_149a1c862dfd4dc5`. O URI foi definido explicitamente; nenhuma conexão implícita a `localhost:27017` foi usada. O backend reiniciado foi apontado explicitamente à mesma base. Isso verifica persistência entre reinícios do processo neste ambiente, mas não failover de replica set nem equivalência com produção.

Os três testes E2E ignorados pela suíte geral foram `admin-import.spec.ts`, `quiz-api-restart-history.spec.ts` (executado separadamente com a condição explícita) e `student-submission.spec.ts`. Os testes de importação/submissão foram mantidos fora do modo CI que altera dados; nenhum conteúdo curricular foi importado. O teste de reinício foi executado à parte e passou.

Em uma execução intermediária, o teste de reinício falhou porque sua fixture consultava a versão recém-publicada, sem tentativas, embora a submissão pertencesse à versão anterior. A fixture foi corrigida para preservar e consultar a versão e a chave da tentativa submetida. A validação final após reiniciar o processo passou. Uma tentativa inicial também usou CORS incompleto no servidor local reiniciado; o teste foi repetido com as origens locais de teste configuradas.

## Segurança e recuperação

- O teste E2E verificou que uma submissão persistida com resposta HTTP perdida é recuperada pela mesma chave e não gera novo POST após reabrir o perfil.
- Um contexto de navegador sem o armazenamento anterior recuperou apenas a tentativa mais recente da versão e foi identificado como tal, sem afirmar que corresponde a uma intenção específica.
- O endpoint não consome tentativas e não inclui gabarito, explicações ou campos administrativos.
- A revisão continua autorizada no servidor após três tentativas; o renderer não é a fonte de verdade.
- O teste de `student-progress` continua tratando conclusão como progresso de leitura; a recuperação não chama o endpoint genérico de progresso.
- A suíte verificou autenticação e isolamento por usuário na superfície de quiz. Não foi acessado ambiente de produção.

## Ressalvas e pendências

1. Sem chave de idempotência ou tentativa já persistida, não há recuperação exata entre dispositivos; o resultado é `unknown` até que uma tentativa apareça ou o aluno tome uma nova ação explícita.
2. Não existe estado persistente `pending`, pois não há reserva separada da atualização atômica. A API informa que o resultado ainda pode estar em processamento.
3. O MongoDB local standalone não prova failover, replicação ou configuração efetiva de produção.
4. A flag permanece desativada por padrão; a configuração de implantação e a topologia de produção continuam por validar.
5. Pontuação agregada continua visível e pode permitir inferência parcial em quizzes pequenos, conforme política aprovada.

## Integridade e estado

- JSON curricular: SHA-256 `43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2`, sem alteração nesta etapa.
- Nenhuma árvore curricular, fonte original, contrato intermediário ou banco compartilhado foi alterado.
- Nenhum commit foi criado.

Parecer: apto para homologação técnica da recuperação no ambiente isolado, com ressalvas operacionais e sem autorização para ativação ou alteração dos pré-requisitos curriculares.

