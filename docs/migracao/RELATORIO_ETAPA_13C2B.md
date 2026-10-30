# Relatório — Etapa 13C.2B

Data: 2026-10-28

Escopo: endurecimento e homologação do fluxo de quizzes, sem ativação operacional e sem importação curricular.

## Resultado

O fluxo específico de quizzes foi validado com frontend e API reais em uma base MongoDB descartável. A suíte dedicada passou: 8 testes Playwright do fluxo principal e 1 teste Playwright executado depois de reiniciar o processo da API. Os 79 testes backend selecionados e os 47 testes unitários frontend passaram.

A etapa fica **concluída com ressalvas de homologação**. Uma execução da suíte E2E geral teve uma falha transitória no teste preexistente `student-progress`; o teste passou quando executado isoladamente. O mypy com imports completos continua reportando 13 erros em módulos preexistentes fora do código alterado nesta etapa. A aprovação desta etapa não habilita produção.

## Pré-voo e preservação

- Worktree: `C:\Users\Joao\.codex\worktrees\fase1-migracao\trilhacodeprod`.
- Branch: `migracao-estrutura`.
- HEAD: `147dc68b81169f66b0ba3802fa2f26e5130923a3`.
- O índice permaneceu vazio; nenhum commit foi criado.
- Alterações locais e artefatos não rastreados das etapas anteriores foram preservados.
- O SHA-256 do JSON curricular permaneceu `43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2`, igual ao pacote `trilhacode.import_bundle/1.0` informado.
- Não houve acesso à instância MongoDB que escuta em `127.0.0.1:27017`, nem a banco de produção.

## Alterações desta etapa

Os arquivos de implementação e os testes a seguir já faziam parte do estado local não commitado das etapas anteriores; foram preservados e atualizados apenas no escopo autorizado:

- `frontend/src/components/student/NodeReader.tsx`
- `frontend/src/components/blocks/QuizApiSession.tsx`
- `frontend/src/components/blocks/QuizApiSession.test.tsx`
- `frontend/src/lib/quizFeature.ts`
- `frontend/src/lib/quizFeature.test.ts`
- `frontend/e2e/quiz-api-real.spec.ts`
- `frontend/e2e/quiz-api-restart-history.spec.ts` (novo teste de reinício)

Não foram alterados backend, contrato intermediário, JSON, árvores curriculares, regras globais de progresso ou configuração de produção. Os dois relatórios desta etapa são novos: este arquivo e `MATRIZ_HOMOLOGACAO_QUIZZES.md`.

## Comportamento da feature flag

`isQuizApiEnabled` trata flag ausente e `false` como desativadas. Nesse estado, o renderer não tenta corrigir quizzes com campos que a API pública omite, não mostra aprovação ou gabarito local e não envia conclusão avaliativa ao progresso genérico. O quiz recebe um aviso acessível de indisponibilidade; os blocos de teoria continuam visíveis. O registro genérico de visita/leitura continua sendo progresso de leitura, não aprovação de avaliação.

Com flag `true`, o renderer usa a API de quiz. Sem resposta da API, apresenta erro recuperável e mantém as respostas locais; não recorre à correção insegura no navegador. A submissão autoritativa, a pontuação, a aprovação e a liberação de revisão vêm do servidor.

Foram executados builds Vite em diretórios temporários novos para as três configurações — variável ausente, `false` e `true`. Cada build concluiu e produziu 1.613 arquivos; nenhum `dist` do repositório foi sobrescrito. Também foram exercitados em desenvolvimento os servidores com flag ausente, falsa e verdadeira. O único arquivo de configuração de ambiente encontrado no frontend foi `.env.example`, com `VITE_QUIZ_API_ENABLED=false`. Configuração efetiva de implantação não foi acessada; não se afirma que o bundle de qualquer ambiente publicado foi inspecionado.

## Recuperação e idempotência no navegador

A intenção pendente de envio agora fica em `localStorage`, com leitura compatível e migração do registro legado em `sessionStorage`. Ela guarda apenas a versão, a chave de idempotência e as respostas selecionadas; não guarda gabaritos, notas ou explicações. Se não for possível persistir a intenção antes do envio, o frontend não envia a tentativa.

Timeout antes da gravação mantém a intenção sem consumir uma tentativa. Quando o servidor grava e a resposta se perde, o retry reutiliza a mesma chave e o mesmo payload; o backend retorna a mesma tentativa. Cliques concorrentes são bloqueados na interface e a idempotência do servidor continua sendo a proteção autoritativa. Uma nova tentativa deliberada recebe outra chave.

O teste Playwright real cobriu fechamento e reabertura do navegador usando o mesmo perfil persistente. Outro teste cobriu a recuperação do histórico no navegador depois de reiniciar a API mantendo a mesma base. Não existe, porém, um endpoint que reconstrua a chave de idempotência depois que o aluno apaga os dados do site, usa outro perfil/dispositivo ou perde o armazenamento local. O histórico não identifica uma intenção ainda sem resultado de forma suficiente para refazer com segurança esse payload. Nesses casos o frontend não inventa sucesso nem cria uma nova tentativa automaticamente; a recuperação exata requer uma extensão mínima da API para consultar o estado da submissão por uma chave/identidade recuperável.

## Ambiente MongoDB e concorrência

Os testes usaram exclusivamente um MongoDB 9.0.2 iniciado para esta execução em `127.0.0.1:27028`, replica set de um membro (`trilha_c2b`), com banco de nome exclusivo da execução. URI sanitizada: `mongodb://127.0.0.1:27028/?replicaSet=<replica-isolado>`; os testes pytest usaram conexão direta ao mesmo membro local. A migração 0003 foi aplicada nessa base descartável; `/ready` informou `migration_version: 3`.

O servidor principal e um segundo servidor de teste com limite reduzido compartilharam somente esse banco descartável. A configuração de 2 leituras por minuto foi exclusiva do processo de teste e de um usuário separado. O endpoint real retornou `429` e `Retry-After`; a interface mostrou o aviso e respeitou a espera.

Os 79 testes backend selecionados passaram contra essa infraestrutura, incluindo submissões concorrentes, limite de três tentativas, repetição com a mesma chave, conflito para payload diferente, falha antes da escrita, índices e retry após reinício de processo. O teste de histórico pós-reinício no navegador também passou. O replica set tinha um único membro: isso prova persistência/reinício e a atomicidade exercitada nesse ambiente, mas **não** comprova failover de replica set multi-membro ou topologia de produção. A migração 0003 não foi aplicada em ambiente real.

## Segurança observada

- O teste HTTP real confirmou que a resposta pública não contém `correct_index`, resposta correta, explicação, `content_hash` ou chave de gabarito.
- Antes da terceira tentativa válida, revisão recusada pelo servidor e resultados/histórico não expuseram explicações nem gabarito.
- Após a terceira tentativa válida, o servidor liberou a revisão; a política de três tentativas, aprovação a 70% e melhor nota continuou aplicada.
- Submissões sem autenticação foram recusadas; histórico e revisão são consultados no contexto da sessão autenticada.
- Campos de nota, aprovação e número de tentativa enviados pelo cliente foram rejeitados.
- O teste de flag desativada confirmou ausência de correção local e de envio de conclusão avaliativa ao endpoint genérico de progresso.
- A pontuação agregada continua visível após cada tentativa e pode permitir inferência parcial em quizzes muito pequenos. Essa limitação foi registrada, sem alterar a política aprovada.
- Logs HTTP do serviço não registraram respostas corretas nem payloads de correção nos cenários verificados. Isso não substitui revisão de observabilidade da implantação.

## Testes e verificações

| Verificação | Resultado |
|---|---|
| `npm.cmd run test -- --reporter=dot` | 47 testes em 7 arquivos aprovados |
| `npm.cmd run typecheck` | aprovado |
| `npm.cmd run lint` | aprovado |
| ESLint dos dois arquivos E2E de quiz | aprovado |
| Playwright `quiz-api-real.spec.ts`, Chromium, serviços reais | 8/8 aprovados |
| Playwright `quiz-api-restart-history.spec.ts`, após reinício da API | 1/1 aprovado |
| Testes backend de quiz, segurança, autenticação, concorrência e contratos, Mongo descartável explícito | 79 aprovados |
| Ruff nos módulos/testes backend pertinentes | aprovado |
| `ruff format --check` nos 7 arquivos backend pertinentes | aprovado |
| Mypy focado nos 3 módulos de quiz backend | aprovado, sem problemas |
| Compilação Python dos módulos/testes pertinentes | aprovada |
| Builds Vite temporários: flag ausente/false/true | 3/3 aprovados, 1.613 arquivos cada |
| `git diff --check` | aprovado; Git emitiu somente aviso de conversão LF/CRLF do JSON já modificado anteriormente |

Uma execução anterior da suíte E2E geral, com 13 testes, terminou com 10 aprovados, 2 skips e uma falha em `student-progress` no fluxo combinado. Esse teste passou quando repetido isoladamente. Os dois skips correspondem a `admin-import.spec.ts` e `student-submission.spec.ts`, protegidos por `test.skip(!CI)` para não mutarem a base fora do modo CI. A suíte geral não foi declarada totalmente verde. O teste específico de quizzes e o teste de reinício passaram separadamente contra os serviços reais.

O mypy com imports completos apontou 13 erros em seis módulos preexistentes (`database.py`, `audit.py`, `services/common.py`, `services/auth.py`, `learning.py`, `integrity.py`). A análise coincide com a ressalva registrada na etapa 13C.2A; os módulos novos/alterados de quiz passaram no mypy focado. Não foram enfraquecidas verificações nem alteradas dependências/locks.

## Pendências e parecer

1. Para recuperação depois de limpar o armazenamento local ou trocar de dispositivo, decidir e implementar uma consulta segura de estado de submissão/idempotência.
2. Repetir a suíte E2E geral em CI/ambiente limpo e esclarecer a falha transitória do teste `student-progress`.
3. Validar a topologia MongoDB representativa do ambiente pretendido, incluindo failover multi-membro, antes de alegar equivalência operacional.
4. Verificar o valor efetivo da flag no processo de implantação antes de qualquer ativação.
5. Considerar a inferência limitada de gabarito pela pontuação agregada em quizzes com poucas questões.

O fluxo de quiz foi testado com sucesso no ambiente isolado, mas esta etapa não autoriza ativação para alunos reais. O JSON legado permaneceu byte a byte no SHA informado; nenhum conteúdo curricular foi importado.
