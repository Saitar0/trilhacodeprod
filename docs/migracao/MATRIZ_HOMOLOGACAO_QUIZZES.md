# Matriz de homologação — quizzes, Etapa 13C.2B

Ambiente: worktree `migracao-estrutura`, HEAD `147dc68b81169f66b0ba3802fa2f26e5130923a3`; testes executados em 2026-10-28. Nenhum cenário acessou produção.

## Comportamento funcional e segurança

| Área | Evidência executada | Resultado | Estado |
|---|---|---|---|
| Flag ausente | Playwright, Vite sem `VITE_QUIZ_API_ENABLED` | Quiz indisponível com mensagem acessível; teoria visível; sem correção local ou gabarito | Aprovado |
| Flag `false` | Playwright e build de produção temporário | Mesmo estado seguro da flag ausente; sem envio de conclusão avaliativa ao progresso genérico | Aprovado |
| Flag `true` | Playwright e build de produção temporário | Carrega e submete pela API; erro da API não ativa fallback local | Aprovado |
| Conteúdo público | Captura da resposta HTTP real do quiz | Sem índice correto, resposta, explicação, chave de resposta ou hash do gabarito | Aprovado |
| Tentativas e correção | API real: 1ª, 2ª e 3ª tentativa; score 70%; reprovação; melhor nota | Servidor calcula; não aprova antes do limite; preserva melhor nota e histórico | Aprovado |
| Limite | API real, submissão após a 3ª tentativa | 4ª tentativa rejeitada | Aprovado |
| Revelação | Resposta pública, tentativa, histórico e revisão reais | Sem gabarito/explicação antes da 3ª; revisão disponível após a 3ª | Aprovado |
| Payload adulterado | HTTP real com `passed`, `score_percent` e `attempt_number` do cliente | Payload rejeitado | Aprovado |
| Autenticação e isolamento | Requests anônimos e consulta de outro usuário | Anônimo rejeitado; histórico administrativo/terceiro não expõe tentativas do aluno | Aprovado |
| Indisponibilidade | API real abortada no navegador com flag ligada | Erro recuperável; respostas mantidas; sem correção local | Aprovado |
| Rate limit | API real isolada, 2 leituras/minuto, usuário dedicado | HTTP 429 com `Retry-After`; UI informa limite e aguarda antes de permitir nova leitura | Aprovado |
| Replay depois de timeout | API grava tentativa; resposta é abortada no navegador; retry com a mesma intenção | Mesmo `Idempotency-Key`, mesmo ID de tentativa; não consome tentativa adicional | Aprovado |
| Retry antes da escrita | Requisição interrompida antes do backend | Intent fica pendente e retém respostas/chave | Aprovado |
| Clique duplo | Dois eventos de submissão no mesmo formulário | Uma requisição de tentativa observada | Aprovado |
| Fechar/reabrir navegador | Perfil persistente Chromium | Intent recuperada e reenviada com a mesma chave | Aprovado |
| Reinício da API | Playwright real após parar e iniciar Uvicorn com a mesma base | Histórico de 3 tentativas recuperado; ID/nota da 2ª conferidos na API; versão ativa permanece independente | Aprovado |
| API reiniciada entre processos backend | Teste de integração backend real | Retry idempotente sobre tentativa persistida | Aprovado |
| Reload comum | Página real recarregada com tentativa pendente | Chave e payload persistidos e reusados | Aprovado |
| Sessão expirada | Cookie removido e API real devolve 401 | UI apresenta sessão expirada; não tenta corrigir localmente | Aprovado |
| Histórico protegido | Histórico real antes da revisão | Pontuação/versão sem chave, explicação ou campos administrativos | Aprovado |
| Armazenamento apagado/outro dispositivo | API atual não oferece lookup recuperável por intenção | Não há recuperação exata demonstrada; UI não inventa sucesso nem abre nova tentativa | Pendência de API |
| Pontuação agregada | Quiz pequeno pode reduzir o espaço de inferência | Score continua visível conforme decisão de produto; inferência parcial possível | Risco residual documentado |

## Persistência e concorrência

| Verificação | Ambiente | Resultado |
|---|---|---|
| Duas, três e quatro submissões concorrentes | MongoDB descartável, replica set local de um membro | Concorrência respeitou três tentativas; não houve número duplicado |
| Mesma chave, mesmo payload | MongoDB descartável | Reproduziu a tentativa persistida sem consumir nova tentativa |
| Mesma chave, payload diferente | MongoDB descartável | Conflito 409 |
| Falha antes da escrita | MongoDB descartável | Não consumiu tentativa |
| Retry após persistência e após reinício do processo | MongoDB descartável | Resultado anterior recuperável por idempotência |
| Índices e migração 0003 | Banco descartável exclusivo | Migração aplicada; health report `migration_version: 3`; testes pertinentes passaram |
| Topologia | MongoDB 9.0.2, replica set de um membro | Sem teste de failover multi-membro; não representa prova de HA de produção |

## Configuração e builds

| Configuração | Como foi exercitada | Resultado |
|---|---|---|
| Desenvolvimento — flag ausente | Vite em porta de teste separada | Quiz marcado indisponível; leitura restante funcional |
| Desenvolvimento — `false` | Vite em porta de teste separada | Sem correção local, revelação ou conclusão avaliativa |
| Desenvolvimento — `true` | Vite com backend descartável | API autoritativa usada |
| Build — ausente | Vite production build para diretório temporário exclusivo | Passou, 1.613 arquivos |
| Build — `false` | Vite production build para diretório temporário exclusivo | Passou, 1.613 arquivos |
| Build — `true` | Vite production build para diretório temporário exclusivo | Passou, 1.613 arquivos |
| Implantação | Nenhum ambiente/segredo de implantação consultado | Valor efetivo no deploy não verificado; a flag continua sem habilitação operacional |

`frontend/.env.example` contém `VITE_QUIZ_API_ENABLED=false`. Os bundles de build foram gravados somente sob `%TEMP%`; cada diretório foi criado para esta execução.

## Execuções e limitações de regressão

| Comando/cenário | Resultado |
|---|---|
| `npm.cmd run test -- --reporter=dot` | 47/47 testes, 7 arquivos |
| `npm.cmd run typecheck` | Passou |
| `npm.cmd run lint` | Passou |
| ESLint em `quiz-api-real.spec.ts` e `quiz-api-restart-history.spec.ts` | Passou |
| Playwright `quiz-api-real.spec.ts`, API e frontend reais | 8/8 passou |
| Playwright pós-reinício `quiz-api-restart-history.spec.ts` | 1/1 passou |
| Testes backend selecionados | 79/79 passou com `MONGO_URL_TEST` explícita apontando à base descartável |
| Ruff e `ruff format --check` em módulos backend pertinentes | Passaram; 7 arquivos já formatados |
| Mypy focado em `routes_quizzes.py`, `schemas/quizzes.py`, `services/quizzes.py` | Passou |
| Mypy com imports completos | 13 erros em seis módulos preexistentes: `database.py`, `audit.py`, `services/common.py`, `services/auth.py`, `learning.py`, `integrity.py` |
| Compilação Python e `git diff --check` | Passaram |
| Suíte E2E geral, 13 testes na execução registrada | 10 passaram; 2 skips existentes; 1 falha transitória em `student-progress`; teste isolado passou posteriormente |

Os dois skips da suíte geral são condicionados a `CI` em `admin-import.spec.ts` e `student-submission.spec.ts`. O teste de reinício foi executado separadamente e passou. A falha da suíte geral não foi atribuída ao fluxo de quiz, mas permanece uma falha de regressão a esclarecer antes de declarar a suíte global completamente verde.

## Ambiente descartável

- MongoDB: 9.0.2.
- Topologia: replica set de um membro chamado `trilha_c2b`.
- Endereço sanitizado: `mongodb://127.0.0.1:27028/?replicaSet=<replica-isolado>`.
- Banco: nome exclusivo da execução; não reutiliza dados reais.
- API: portas locais 18000/18001; o processo em 18001 utilizou limite reduzido apenas para o teste de 429.
- Frontend: portas locais 5174–5177; nenhuma foi usada como ativação para alunos.
- Migração 0003: aplicada somente no banco descartável; pronta indica versão 3.
- Não se afirma teste de failover multi-membro nem conexão a banco de produção.

## Limites de homologação

1. O modo persistido do navegador permite retry após fechar/reabrir o mesmo perfil. A limpeza de armazenamento ou troca de dispositivo não pode recuperar a intenção exata com a API atual.
2. O teste de falha após gravação intercepta a resposta no ponto HTTP do navegador. É um teste controlado com API real, não uma simulação de corte físico da rede.
3. A pontuação agregada permite inferência parcial em quizzes de pouquíssimas questões.
4. A topologia MongoDB testada não cobre failover de produção.
5. A flag não foi ativada em produção e nenhuma configuração efetiva de implantação foi consultada.
6. A suíte E2E geral ainda tem a ocorrência isolada descrita acima; somente os testes de quiz e pós-reinício estão totalmente verdes nesta execução.
