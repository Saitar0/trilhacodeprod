# Beta 6.1 — resultado do navegador

## Evidência

Playwright Chromium executou `frontend/e2e/beta6-1-learning-journey.spec.ts` contra o Vite e o Uvicorn iniciados dentro do runner isolado, conectados ao MongoDB 7 descartável. Resultado: **1 passed** (uma worker, aproximadamente 23 segundos). A origem do navegador, API e cookies foi alinhada em `127.0.0.1` dentro do mesmo namespace. Chamadas HTTPS externas do browser foram abortadas.

## Jornada exercitada

1. Aluno sintético autenticou-se pela tela real de login.
2. A interface consultou a árvore e a unidade por endpoints reais.
3. A aula exibiu título e teoria; a resposta HTTP não continha gabarito, rubrica, resposta privada ou metadado de importação.
4. O aluno iniciou o quiz, selecionou alternativa e recebeu feedback calculado pelo backend.
5. O aluno enviou exercício e viu estado enviado/aguardando correção.
6. Um editor sintético sem escopo tentou a fila e o detalhe: `403` e `404`.
7. O avaliador autorizado consultou a fila, abriu rubrica e resposta de referência restritas, reivindicou a submissão e gravou feedback/aprovação.
8. O aluno autenticou-se novamente, recebeu seu feedback, sem dados do avaliador reservados, rubrica ou resposta de referência.
9. Recarregou a aula; a API retornou progresso concluído para quiz e exercício e a interface manteve o feedback.

O spec também verifica explicitamente a resposta HTTP de grade e a consulta de `/api/submissions/mine`, evitando considerar somente texto local da interface como persistência.

## QA do frontend executado no mesmo runner

* TypeScript: `npm run typecheck` passou.
* ESLint: `npm run lint` passou.
* Vitest: 9 arquivos, **29 testes aprovados**.
* Build: `npm run build` passou.
* O chunk de entrada ficou em **505,92 kB** (gzip 162,66 kB), acima do limite de aviso de 500 kB. O build concluiu; otimização de bundle fica como melhoria posterior.

## Limites

É uma jornada desktop Chromium em fixture sintética. Não equivale a homologação visual abrangente, teste mobile/accessibilidade, beta com participantes reais ou prova IAM operacional. O avaliador usou o escopo experimental por trilha configurado no banco descartável. Não houve publicação editorial fora da fixture.
