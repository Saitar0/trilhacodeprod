# Relatório — Etapa 13C.1A: endurecimento do backend de quizzes

## Resultado

**PARCIALMENTE CONCLUÍDA PARA HOMOLOGAÇÃO OPERACIONAL.** A limitação de requisições foi integrada ao mecanismo existente e a recuperação/idempotência foi exercitada em MongoDB descartável, inclusive após iniciar outro processo da API. Os testes do backend passaram. A etapa não pode alegar homologação completa de failover porque o ambiente disponível é MongoDB standalone, sem replica set. Também permanece sem decisão a semântica dos pré-requisitos curriculares que possam exigir aprovação avaliativa.

Não foram alterados renderer, importador, JSON curricular definitivo, contrato intermediário, conteúdo migrado, fontes curriculares ou banco de produção. Não houve commit.

## Pré-voo e integridade

- Worktree: `C:\Users\Joao\.codex\worktrees\fase1-migracao\trilhacodeprod`.
- Branch: `migracao-estrutura`.
- HEAD: `147dc68b81169f66b0ba3802fa2f26e5130923a3`.
- Índice vazio no pré-voo e sem caminhos staged no encerramento.
- Havia alterações locais de 13C.1 e artefatos não rastreados de etapas anteriores. Foram preservados; nenhum arquivo foi limpo, descartado ou incluído em commit.
- Árvore migrada: 2.890 arquivos, sem alterações atribuíveis a esta execução.
- JSON legado `docs/courses/trilhacode/trilha-code-bulk-import.json`: SHA-256 `43125c5902168def6359e514ad80602a1f7579157e1a0bb16f1f2212ee4c18e7`, igual ao valor do manifesto de integridade.
- Manifesto de integridade 12D: SHA-256 `C3F5AA792641408EB66FC80CF801206DE4E1DEEF2130A5A5C436C8D9ADE58055`; os 12 artefatos listados continuam validados pelo manifesto.
- `git diff` não aponta alterações em `Conteudos_migrado/`, JSON legado ou `contrato_intermediario/`.

## Arquivos desta etapa

| Caminho | Alteração |
|---|---|
| `.env.example` | Documenta os cinco limites configuráveis para endpoints de quiz. |
| `backend/settings.py` | Adiciona limites positivos validados por Pydantic; inclui anotação local `list[str]` necessária ao mypy. |
| `backend/server.py` | Padroniza respostas HTTP 429 com código `rate_limited`. |
| `backend/services/quizzes.py` | Aplica os buckets autenticados por usuário aos endpoints de leitura, tentativa, histórico, revisão e publicação; adiciona `Retry-After`; retries sequenciais já persistidos contornam somente o consumo do bucket de tentativa. |
| `backend/tests/test_quizzes.py` | Amplia testes HTTP e MongoDB descartável para limites, progresso, migração, concorrência, falhas e reinício do processo. |
| `docs/migracao/IMPLEMENTACAO_BACKEND_QUIZZES.md` | Registra limites, configuração e resposta 429 atuais. |
| `docs/migracao/ESPECIFICACAO_QUIZZES.md` | Atualiza o status da proposta de rate limiting. |
| `docs/migracao/MATRIZ_SEGURANCA_QUIZZES.md` | Matriz de riscos, evidências, pendências e escopo dos skips. |
| `docs/migracao/RELATORIO_ETAPA_13C1A.md` | Este relatório. |

Os demais arquivos modificados/rastreados e não rastreados já estavam no worktree antes desta etapa, como artefatos da 13C.1 e etapas anteriores; foram mantidos. O relatório não os atribui a esta implementação.

## Limitação de requisições

Os endpoints usam `services.auth.rate_limit`, que mantém bucket Mongo-backed compartilhado, com identificador derivado por HMAC do usuário autenticado e categoria da rota. O endereço IP não compõe a chave do quiz; o teste repetiu uma submissão de outro IP e recebeu 429 para a mesma identidade. A publicação continua protegida pela permissão `content.publish`.

Limites padrão por minuto: leitura 120, submissão 10, histórico 60, revisão 30 e publicação 10. Os valores podem ser substituídos pelas variáveis `QUIZ_*_LIMIT_PER_MINUTE` listadas na matriz. O algoritmo é token bucket com burst até o limite e refill durante 60 segundos, não uma janela fixa. Respostas limitadas têm HTTP 429, código estável `rate_limited` e `Retry-After` calculado para o próximo token.

O limite de submissões é por usuário e categoria, atravessa quizzes diferentes e não altera o contador avaliativo. Uma repetição sequencial com chave/payload já gravados retorna o resultado existente antes do bucket e não cria nem consome nova tentativa. Uma falha de infraestrutura pode consumir um token de requisição mesmo sem persistir tentativa; o retry idempotente pode aguardar o refill se o bucket se esgotar.

## Falhas, concorrência e recuperação

O serviço não cria uma reserva separada. A atualização condicional de `quiz_progress` incrementa contador e anexa o registro no mesmo documento. Por isso:

- Falha simulada antes do write: o agregado permaneceu em `attempt_count=0`; retry da mesma chave criou exatamente a tentativa 1.
- Falha simulada depois do write confirmado: o processo original perdeu a resposta; outro processo Uvicorn, iniciado durante o teste e ligado ao mesmo banco aleatório `test_<uuid>`, repetiu a chave e devolveu a mesma resposta persistida. O contador ficou em 1.
- Payload diferente para a mesma chave continua resultando em 409.
- Concorrência com duas e três submissões atribuiu números únicos; a regressão existente de quatro submissões manteve exatamente três aceitas e uma rejeitada. O retry concorrente com a mesma chave manteve um único registro.

As falhas foram injetadas na fronteira de persistência; não simulamos perda de pacotes real, timeout do driver após confirmação, encerramento abrupto do MongoDB ou eleição de replica set. A recuperação de reinício do processo da API é comprovada no ambiente local; garantias de failover do banco seguem pendentes.

## MongoDB e migração 0003

O harness usa `MONGO_URL_TEST` local, converte a URI para conexão direta, escolhe banco aleatório com prefixo `test_` e descarta somente esse banco no teardown. Um segundo banco com prefixo seguro foi criado e removido para verificar dados duplicados. Nenhum banco compartilhado ou real foi acessado.

O servidor de teste informou **MongoDB 9.0.2, standalone**. `compose.yaml` declara imagem `mongo:7`, mas essa versão e a topologia-alvo não foram executadas neste ambiente. `0003_quiz_attempts.up()` foi chamada duas vezes em banco descartável e manteve os mesmos dois índices únicos. Em outro banco descartável, duplicatas prévias de `(quiz_id, content_hash)` fizeram a criação do índice único falhar sem apagar os documentos nem criar o índice conflitante. O runner grava a versão da migração somente depois que `up()` termina; o preflight já detecta duplicatas antes da implantação. Duplicatas reais exigem intervenção explícita.

Como o mecanismo usa updates atômicos de documento único e não transações multi-documento, o teste standalone verifica a operação CAS local. Ele não demonstra garantias de failover, write concern ou disponibilidade do deployment em replica set.

## Progresso legado e pré-requisitos

`POST /api/progress` aceita status de leitura e `data` arbitrária. A data de conclusão é gerada pelo servidor e não é um campo do request. Um teste enviou `passed`, `score_percent` e `correct_answers` em `data`; o quiz continuou com `passed=false`, zero tentativas e revisão 403. O serviço de quiz não consulta nem escreve o endpoint genérico para pontuação/aprovação.

Ainda assim, `learning.track_locks` usa registros legados `progress.status="completed"` para destravar relações de pré-requisito. A relação atual não informa se exige leitura/conclusão ou aprovação de quiz. Não alteramos essa regra global nem inventamos semântica: permanece pendente decidir se o modelo distinguirá pré-requisito avaliativo e qual evidência autoritativa será exigida. Portanto, o estado de aprovação do quiz não é falsificável por `POST /api/progress`, mas o bloqueio de uma relação genérica que tenha sido editorialmente pensada como aprovação não pode ser garantido com o esquema atual.

## Testes e verificações

Ambiente: Python 3.13; API de teste com MongoDB local descartável versão 9.0.2 standalone.

| Verificação | Comando | Resultado |
|---|---|---|
| API, autenticação, autorização, progresso, persistência e quizzes | `py -3.13 -m pytest tests -q --tb=short` | **115 passed**. Inclui os testes novos de rate limit, migração, concorrência e recuperação em processo novo. |
| Unitários | `py -3.13 -m pytest unit_tests -q -rs --tb=short` | **206 passed, 37 skipped**. |
| Skip de Docker | `unit_tests/test_g2_docker_api_contract.py` | 1 skip: Docker Engine não disponível; contrato executado no CI Linux. |
| Skips POSIX | `unit_tests/test_g2_runner.py` | 36 skips: requer Bash POSIX, `jq` e `flock`, ausentes no ambiente Windows. |
| Ruff lint | `py -3.13 -m ruff check backend` | Passou. |
| Formatação do código novo/trechos alterados | `ruff format --check` em `services/quizzes.py`, `tests/test_quizzes.py` e ranges alterados de `server.py`/`settings.py` | Passou. |
| Formatação arquivo inteiro | `ruff format --check backend/server.py backend/settings.py` | Ainda aponta deriva anterior de formatação em trechos não alterados; não formatamos o arquivo inteiro para evitar churn fora das mudanças necessárias. |
| Tipagem | `py -3.13 -m mypy --explicit-package-bases --follow-imports=silent --disable-error-code=import-not-found services/quizzes.py settings.py server.py tests/test_quizzes.py` | Passou, 4 arquivos sem problemas. |
| Compilação Python | `py -3.13 -m compileall -q ...` nos quatro módulos/testes modificados | Passou. |
| Diff | `git diff --check` | Passou. |
| Dependências | `py -3.13 -m pip check` | `No broken requirements found`. Versões instaladas `google-api-core 2.33.0`, `grpcio-status 1.71.2`, `grpcio 1.84.0` satisfazem as restrições examinadas; nenhum lock/dependency foi alterado. |

Os 37 skips são limitações explícitas de ambiente/capacidade, não testes de quiz ignorados. Não alteramos marcações de skip nem enfraquecemos verificações.

## Prontidão e pendências

**A prontidão é parcial, não homologação de produção.** Os controles aplicados e testados em MongoDB standalone cobrem limites, correção autoritativa, isolamento, retries, restart da API, migração e concorrência single-document. Antes de ativar em produção ou avançar a integração funcional, ainda é necessário:

1. Executar a bateria em replica set com versão/topologia compatíveis com a implantação, incluindo failover/write concern.
2. Decidir e modelar se algum pré-requisito exige aprovação de quiz em vez de progresso de leitura.
3. Homologar configuração de limites no ambiente de implantação e monitorar 429/refill.
4. Integrar o renderer na Etapa 13C.2, sem revelar chaves antecipadamente.
5. Manter explícita a inferência possível da nota em quizzes de uma questão, conforme a regra de nota imediata aprovada.

O frontend, JSON curricular, importador, MongoDB real e árvores homologadas permaneceram fora de escopo e inalterados.
