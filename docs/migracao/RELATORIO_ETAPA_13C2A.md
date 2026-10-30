# Relatório — Etapa 13C.2A: homologação E2E de quizzes

## Resultado

**Conclusão parcial: os seis testes ponta a ponta passaram no ambiente isolado, mas a homologação operacional continua bloqueada.** O fluxo com a API real cumpriu a política de tentativas, correção, revelação e idempotência. O cenário com a feature flag desligada também confirmou uma incompatibilidade do fluxo legado: a API de conteúdo remove `correct_index`, então o renderer antigo não consegue reconhecer uma resposta correta. A flag não foi ativada fora do ambiente isolado; a configuração efetiva do build de produção não foi inspecionada.

## Pré-voo e preservação

- Worktree: `C:\Users\Joao\.codex\worktrees\fase1-migracao\trilhacodeprod`.
- Branch: `migracao-estrutura`.
- HEAD: `147dc68b81169f66b0ba3802fa2f26e5130923a3`.
- O índice estava vazio no início. As alterações rastreadas e não rastreadas já existentes foram preservadas; não houve commit.
- As regressões curriculares e o JSON não foram editados por esta etapa.
- O código novo desta etapa limita-se ao teste `frontend/e2e/quiz-api-real.spec.ts` e a este relatório e à matriz E2E.

## Ambiente isolado

| Componente | Configuração verificada |
|---|---|
| Sistema | Windows, worktree local autorizado |
| Node.js / npm | 24.20.0 / 11.19.0 |
| Playwright | 1.64.1, Chromium |
| Python | 3.13 |
| FastAPI / Pydantic / PyMongo | 0.141.1 / 2.13.5 / 4.17.0 |
| Backend | `127.0.0.1:18000` |
| Frontend flag ligada | `127.0.0.1:5174`, modo Vite `e2e_on` |
| Frontend flag desligada | `127.0.0.1:5175`, modo Vite `e2e_off` |
| MongoDB descartável | 9.0.2, `127.0.0.1:27018`, replica set local de um membro |
| Banco do teste principal | Nome aleatório com prefixo `trilha_quiz_e2e_13c2a2_`; sem dados reais |

A migração `0003_quiz_attempts` foi aplicada no MongoDB descartável; `/ready` respondeu `ok: true` e `migration_version: 3`. Nenhum currículo foi importado. O teste com replica set de um membro prova o comportamento neste ambiente, mas não comprova failover ou topologia multi-membro da implantação.

Durante uma inicialização preliminar, antes de o processo do backend receber a configuração explícita de teste, ele consultou somente a versão do schema no Mongo local padrão `localhost:27017`. O processo foi encerrado imediatamente. Não há evidência de migração, seed ou escrita nessa instância. Como não é possível comprovar se essa instância local corresponde a dados de produção, isso fica registrado como ressalva de ambiente; todas as execuções E2E e regressões documentadas abaixo apontaram explicitamente para `27018`.

## JSON curricular: reconciliação sem escrita

SHA-256 real do arquivo no worktree autorizado:

`43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2`

O parser `validate_import_bundle_json` aceitou o arquivo como `trilhacode.import_bundle/1.0`; a serialização por `canonical_import_bundle_json` foi byte a byte idêntica ao arquivo. O pacote declara 10 fases, 572 nós, 3.431 blocos, 15 projetos, 501 blocos `answer_key`, 133 arquivos Markdown de origem e 4.311 registros de mapeamento.

A outra soma, `43125c5902168def6359e514ad80602a1f7579157e1a0bb16f1f2212ee4c18e7`, aparece no pacote atual como `source.legacy_json_sha256_before_conversion` e em `integrity.global_counts.legacy_json_sha256`: é o hash da entrada JSON legada anterior à serialização em bundle, não o hash do arquivo atual. O arquivo atual está marcado como alterado no Git antes desta etapa; esta execução não o sobrescreveu nem o regenerou.

Há cópias divergentes do JSON em outros worktrees registrados: a cópia autorizada tem o bundle completo acima; outras cópias examinadas usam o formato legado `{track, options, nodes, relations}` e têm hashes `43125…`, `8af320…` ou `e47721…`. Isso confirma divergência entre worktrees, mas não torna ambíguo o resultado do worktree autorizado: seu bundle é válido, canônico e contém o hash da entrada legada. Essas cópias não foram alteradas.

## Feature flag

A variável é incorporada ao bundle durante o build. Foram criados builds de produção somente em um diretório temporário fora do repositório, sem alterar `frontend/dist`:

| Build | Valor incorporado em `isQuizApiEnabled` | Resultado |
|---|---:|---|
| `e2e_on` | `"true"` | Ativo apenas no frontend isolado de teste |
| `e2e_off` | `"false"` | Desativado |
| `e2e_absent` | `void 0` | Desativado pelo valor padrão (`value === "true"`) |

O teste com flag desligada não realizou chamadas `/api/quizzes/` e confirmou que o renderer legado recebe conteúdo sem a chave: mesmo a alternativa correta apareceu como “Ainda não.” Isso não ativa a API nem expõe gabarito; é uma limitação funcional do período em que a flag fica desligada. A configuração de produção não foi alterada.

## Testes ponta a ponta

Spec criado: `frontend/e2e/quiz-api-real.spec.ts`. Execução: `npm run test:e2e -- e2e/quiz-api-real.spec.ts`, com frontend, API, autenticação e MongoDB reais do ambiente descartável. Resultado: **6 aprovados, 0 falhos**.

Os cenários verificaram:

1. Login, navegação ao tópico e carregamento das dez questões publicadas.
2. Ausência de `correct_index`, alternativa correta, explicação, hash ou `answer_key` no payload público.
3. Rejeição de cliente anônimo, revisão antecipada (403) e tentativa com `score_percent`/`passed` fornecidos pelo cliente (422).
4. Falha de rede antes da gravação, recarga e reenvio com a mesma chave e payload; a tentativa foi registrada uma vez.
5. Aprovação exatamente em 70% na primeira tentativa, sem liberar revisão.
6. Resposta perdida após gravação, fechamento e reabertura da aba; histórico mostrou a tentativa persistida, retry com mesma chave não duplicou a tentativa.
7. Três tentativas, nota máxima preservada, revisão e explicações somente após a terceira, e quarta submissão recusada (409).
8. Isolamento do histórico: o usuário administrativo não recebeu as tentativas da conta de estudante.
9. Sessão expirada (401), API indisponível sem fallback de correção local e apresentação acessível de erro recuperável.
10. Burst real de 30 consultas gerando HTTP 429 com `Retry-After`, respeitado pelo cliente; burst de publicação também atingiu 429.
11. Nova versão imutável com contador reiniciado e republicação idêntica reutilizando a versão existente.

Depois da suíte, o backend foi reiniciado. O mesmo payload e chave da segunda submissão foram reenviados por uma chamada de API usando o registro temporário de replay. A API retornou o mesmo `attempt_id`, número 2 e histórico ainda com três itens. Isso comprova a recuperação do servidor por retry após reinício neste ambiente; não comprova que a interface recupere a chave pendente depois de fechar a aba.

As falhas de rede foram simuladas pelo navegador abortando a conexão em pontos específicos; os fluxos de autenticação, quiz, gravação, histórico, versão e revisão foram solicitações reais à API. Não foi usado mock para os cenários principais.

## Regressões e qualidade

| Comando | Resultado |
|---|---|
| `npm.cmd test -- --reporter=dot` | 45 testes aprovados em 7 arquivos |
| `npm.cmd run typecheck` | aprovado |
| `npm.cmd run lint` | aprovado |
| Builds Vite `e2e_on`, `e2e_off`, `e2e_absent` | 3 builds concluídos em saídas temporárias; constantes conferidas |
| `py -3.13 -m pytest tests/test_quizzes.py tests/test_auth_security.py tests/test_auth_role_refresh.py tests/test_integrity_concurrency.py unit_tests/test_quiz_api_contracts.py unit_tests/test_quiz_grading.py -q --tb=short` | 79 testes aprovados; Mongo descartável em `127.0.0.1:27018` |
| `py -3.13 -m ruff check ...` (seis arquivos backend relacionados) | aprovado |
| `py -3.13 -m ruff format --check ...` | 6 arquivos já formatados |
| `py -3.13 -m compileall -q ...` | aprovado |
| `py -3.13 -m mypy --explicit-package-bases --follow-imports=silent routes_quizzes.py schemas/quizzes.py services/quizzes.py` | aprovado; 3 arquivos |
| mypy sem `--follow-imports=silent` | não aprovado: 13 erros em dependências preexistentes (tipagem de `database.py`, `audit.py`, `services/common.py`, `services/auth.py`, `learning.py` e `integrity.py`) |
| `git diff --check` | aprovado |

Não foi executada a suíte integral de todos os testes do backend, nem testes contra a topologia de MongoDB de produção. A suíte selecionada teve 79 aprovados e nenhum skip reportado. Os 37 skips citados no relatório anterior da 13C.1 não foram reavaliados como parte deste recorte.

## Segurança observada e limitações

- Correção, nota, aprovação e contador foram confirmados vindo do servidor; o payload do cliente com nota/aprovação foi recusado.
- Respostas corretas e explicações não apareceram no payload público, resultados ou histórico antes da terceira tentativa. A revisão autenticada passou a retornar o gabarito após o esgotamento.
- O backend aplicou isolamento por usuário, tentativas máximas, idempotência e rate limiting nos testes observados.
- A pontuação agregada ainda pode permitir inferência em quizzes de uma questão; a política de produto foi preservada.
- O teste de autorização usou uma segunda identidade administrativa para consultar o histórico do estudante e recebeu total zero. Não foi criado um endpoint de leitura individual de tentativa para testar enumeração de IDs, pois o contrato não o expõe.
- A aba foi fechada e reaberta e o histórico persistido foi confirmado. A chave de idempotência e o corpo de retry após reinício foram fornecidos pelo artefato de teste; a recuperação dessa chave no navegador depois de fechar a aba não foi comprovada. O `sessionStorage` existente não é durável entre abas/sessões.
- Não foi injetado um timeout cronometrado de socket. Foram testadas falha de rede antes do envio chegar à API e perda da resposta depois da gravação, além do replay após reinício.
- A suíte E2E não executou duas ou três submissões de tentativa concorrentes. O limite sequencial, o clique duplicado, bursts de leitura/publicação e as regressões backend foram exercitados; a corrida concorrente de tentativas precisa de teste integrado específico antes da ativação operacional.
- Os logs comuns produzidos pelo backend de teste foram inspecionados; não continham `correct_index`, `answer_key`, texto de explicação ou credenciais de teste. Isso não substitui revisão de logs da implantação.
- O teste confirma uma réplica isolada de um membro, não a disponibilidade/atomicidade operacional de um cluster de produção.

## Parecer

**E2E isolado aprovado; homologação operacional parcial.** A política funcional e as proteções da API passaram no cenário real isolado. Antes da ativação, é necessário decidir como o produto deve se comportar com `VITE_QUIZ_API_ENABLED=false`: hoje o renderer legado não corrige corretamente porque a API oculta sua chave. Também permanece necessária a validação operacional da topologia real de MongoDB, sem usar dados de produção nesta etapa. Nenhuma ativação, importação, alteração do JSON ou commit foi realizado. Um processo preliminar fez apenas a consulta de leitura descrita acima ao Mongo local padrão; sua eventual relação com produção não pôde ser estabelecida. O backend, os frontends e o Mongo de teste foram parados. Os arquivos temporários de build e a pasta de dados descartáveis permaneceram sob `%TEMP%` em `trilha-c2a-build-011fc9af25a446c59deb5865fcd4c2a3` e `trilha-quiz-e2e-de62488551264fdf863827e73f120ba1`; os dois `.env.e2e_*.local` usados para teste foram removidos. Os temporários não estão no repositório.
