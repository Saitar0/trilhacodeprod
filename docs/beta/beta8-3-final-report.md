# Beta 8.3 — Relatório final

## A–B. Resultado executivo e Git

A Beta 8.3 separou, na composição descartável, a API FastAPI e a autoridade editorial em serviços/contêineres diferentes, com PIDs e usuários MongoDB distintos. As rotas existentes W-07 PUT, W-07 POST e W-05 PUT atravessaram comunicação interna autenticada, revalidação de sessão e grant, CAS/fencing e auditoria persistente. A prova reutilizou o serviço real de staging Beta 5 e o bridge experimental das fases anteriores, apenas com lote sintético.

Resultado global: **BETA 8.3 PARCIALMENTE VALIDADA — ISOLAMENTO, INTEGRAÇÃO OU REGRESSÕES PENDENTES**. A fronteira experimental foi demonstrada; não há comprovação de distribuição operacional de segredos, contenção dos writers restantes, Playwright ou regressão histórica completa. Nenhum conteúdo real foi publicado, nenhuma alteração operacional foi feita.

* Base: `167166e311024678a9619b18678bc145c3482d12`.
* Branch: `codex/beta8-3-isolated-editorial-authority`.
* Worktree: `C:\Users\Joao\.codex\worktrees\trilhacode-beta8-3-authority-isolation\trilhacodeprod`.
* Checkout original e demais worktrees: preservados.
* Commits: registrados no histórico local da branch; sem push, PR, merge ou deploy.
* Estado final pretendido: worktree limpa após o commit.

## C–H. Arquitetura, processos, credenciais e startup

Na Beta 8.2, a composição montava o boundary editorial no processo da API. Essa composição tinha uma identidade MongoDB comum, mas não comprovava processo separado para a credencial editorial. A Beta 8.3 acrescenta harness explícito com API, autoridade, MongoDB/replica set e verifier independentes.

| Componente sintético | Privilégio exercitado | Não recebe |
| --- | --- | --- |
| API FastAPI | Leituras e operações comuns permitidas | URI/senha Mongo da autoridade, URI do staging, segredo do stager e credencial root |
| Autoridade | Escritas tipadas nas coleções necessárias, revalidação de IAM e auditoria | Credencial root, identidade de escrita do staging e credencial Mongo da API |
| Stager Beta 5 | Preparação/checkpoint do lote sintético | Credencial editorial privilegiada |
| Leitor de staging | Leitura/verificação do lote preparado | Escrita no staging ou publicação |
| Provisionador/verifier | Root sintético temporário para provisionar/assertar | Não é distribuído aos serviços long-lived |

O runner verificou IDs/PIDs distintos, variáveis e mounts, identidade da imagem, rede interna, ausência de portas publicadas, ausência de volumes persistentes e usuários separados. O MongoDB negou sete tentativas de escrita direta feitas com a identidade da API; negou também operações fora dos privilégios conferidos à autoridade. Essas são credenciais e permissões criadas somente no banco descartável.

Sem os marcadores de composição, os módulos de teste falham antes de importar o servidor/banco. Sem boundary experimental, W-07 PUT/POST e W-05 PUT respondem `503` fail-closed. Isso impede fallback local, mas deixa essas mutações indisponíveis no startup comum. Não se verificou runtime operacional nem compatibilidade de uma futura autoridade operacional.

## I. Entrega A — processos

**AUTORIDADE EDITORIAL ISOLADA POR PROCESSO E CREDENCIAIS EM AMBIENTE DESCARTÁVEL**

Evidência: log final identificou serviços e PIDs diferentes; imagem/processos receberam somente suas variáveis autorizadas; probes autenticados no MongoDB confirmaram fronteiras. O processo API não recebeu a URI privilegiada nem o segredo exclusivo do stager/reader. A autoridade realizou as escritas aprovadas e o API não conseguiu substituí-la escrevendo diretamente.

Limite: esta evidência Docker não prova distribuição, rotação ou ACL de segredos fora do harness.

## J–M. Comunicação, identidade e contrato

API → autoridade usa POST interno por rede Docker privada e HMAC-SHA256 sobre serviço, método, caminho, timestamp, nonce e hash do corpo. Respostas também são assinadas e vinculadas ao nonce. A autoridade rejeita assinatura ausente/inválida, nonce repetido e timestamps fora da janela; indisponibilidade do ledger de replay é negação, não autorização. Não há TLS/criptografia do payload: o transporte só foi exercitado dentro da rede privada descartável.

A rota existente autentica pelo mecanismo FastAPI/JWT, deriva `actor_id`, `session_id` e `token_version` do usuário autenticado e claims validados, sem aceitar esses valores do corpo como autoridade. A autoridade consulta usuário ativo, sessão não revogada/não expirada, versão do token, permissão global requerida e projeção/grant C12 por recurso/escopo; então aplica C8/C12 e participa do guard transacional de sessão/usuário. Um cliente HTTP não consegue assinar o RPC. A API e a autoridade compartilham a chave HMAC sintética para autenticar a relação entre serviços; a API é, portanto, um gateway confiável. Comprometimento total da API não foi modelado como ator não confiável e continua sendo risco de arquitetura/ops.

O contrato fechado admite somente `block.update`, `block.create`, `node.update` e a transição de fixture sintética do staging. Schemas proíbem campos extras, queries, coleções arbitrárias e autorização autodeclarada; payload tem limite. `block.create` vincula ID ao operation ID e só aceita estado draft. Não existe endpoint de comando Mongo genérico.

## N–P. W-07 PUT, W-07 POST e W-05 PUT

As rotas/services existentes foram conectados ao facade RPC sem substituir a validação de aplicação. No harness:

* **W-07 PUT:** request autenticada, grant e sessão válidos, revisão/fence; sucesso, retry idempotente, mesmo ID com payload divergente e revisão concorrente exercitados.
* **W-07 POST:** criação draft com identidade vinculada à operação e escopo revalidado pela autoridade.
* **W-05 PUT:** atualização de unidade através da autoridade e revisão condicional.

Marcadores persistentes `HTTP_W07_PUT`, `HTTP_W07_POST` e `HTTP_W05_PUT` passaram. Esses resultados cobrem as três operações selecionadas, não todos os métodos/endpoints que possam compartilhar W-07/W-05. O restante do inventário C16 não foi migrado nesta fase.

## Q–U. Revogação, CAS, idempotência, auditoria e falhas

Foram exercitados grant ausente/revogado, recurso fora do escopo, usuário admin sem grant, sessão expirada/revogada/deslogada, identidade adulterada no corpo e revisão obsoleta. A checagem de sessão/grant ocorre na autoridade, e o guard de IAM participa da transação da decisão C8, ordenando a revogação testada com a mutação. Na corrida persistente de duas atualizações HTTP, uma venceu (`200`) e outra recebeu conflito (`412`); não houve sobrescrita silenciosa.

Retries do mesmo operation ID/payload retornam recibo idempotente; payload divergente é conflito. A resposta é autenticada. Se a resposta estiver ausente/invalidada, o cliente levanta outcome desconhecido com operation ID para reconciliação e não tenta escrita direta. Auditoria persistiu ator, recurso/track, operação e decisão. O teste de resposta perdida representa retry após resultado durável; não simula queda real da conexão exatamente após commit.

Falha ou ausência da autoridade nunca ativa o boundary local ou credencial privilegiada. O teste offline cobre falha de conexão e outcome desconhecido; a prova persistente exercitou os caminhos de sucesso e conflito.

## V–AB. Entrega B, staging e preservação

**TRÊS OPERAÇÕES EDITORIAIS VALIDADAS ATRAVÉS DA AUTORIDADE SEPARADA**

O harness executou `CurriculumStagingService` Beta 5 para preparar lote sintético com identidade stager. A autoridade, com usuário de leitura do staging, verificou marcador/owner, manifesto, checkpoints e conteúdo persistido, e então chamou o bridge Beta 8.1/Beta 8.2 e `Beta8ExperimentalPromoter` para transição sintética. O guard de sessão/usuário participa da transação experimental. Nenhuma rota/coleção operacional de publicação foi chamada.

**STAGING VALIDADO COM AUTORIDADE SEPARADA NO ESCOPO EXPERIMENTAL**

Persistência demonstrada: retry idêntico sem geração duplicada; duas transições concorrentes do mesmo comando produziram uma confirmação e um replay; adulteração do conteúdo persistido foi negada antes de nova geração. Foi verificada a manutenção da geração anterior. Sentinelas sintéticas de tentativas, submissões e progresso permaneceram iguais. Usuário stage-reader não consegue atualizar o lote; stager não tem acesso às coleções editoriais; a autoridade não tem privilégio `delete` editorial nem publicação operacional.

Limites: a resposta perdida é simulada por retry depois do commit. Reinício real da autoridade durante a transição e falhas naturais de rede não foram exercitados. Staging/prova usa namespace descartável e lote sintético, não a primeira fase real nem a rubrica real.

## AC–AI. Testes, regressões e qualidade

`run-local.ps1` terminou com código 0:

* Offline dentro da imagem de teste e sem rede: **36 passed, 1 skipped**. O skip refere-se ao fixture cuja fonte curricular não está presente no sparse checkout; não conta como prova de leitura de conteúdo real.
* Persistência/HTTP/MongoDB: provisionamento, boundary entre processos, sete negativas diretas de escrita da API, negativas de autoridade/leitor, W-07 PUT/POST, W-05 PUT, nonce replay, CAS concorrente, bridge staging, idempotência, concorrência staging, integridade do lote, revogação e negativas de sessão/grant passaram.
* Cleanup: recursos efêmeros revalidados por label/ID e removidos; contêiner, rede, imagem local e armazenamento temporário não permaneceram.
* O teste de contrato `pytest` da imagem cobre cinco arquivos direcionados, não a suíte completa do backend.
* `git diff --check`, compilação/execução dos módulos Python e validação do Compose foram concluídos pelo harness/build.

**REGRESSÕES PARCIALMENTE VALIDADAS — COBERTURA PENDENTE**

Playwright/frontend não foram executados: a composição não inicia frontend nem prévia curricular. A suíte histórica C8–C16/Beta 5–8.2 completa, Ruff, MyPy, TypeScript, ESLint e build frontend não foram executados. Assim, não se declara regressão de navegador ou cobertura histórica integral.

## AJ–AM. Estado pedagógico, writers e limites

O currículo fonte não foi lido ou alterado nesta fase. Não houve publicação ou promoção operacional. A rubrica real do projeto 3.5 permanece `PROPOSED`; nenhuma conclusão pedagógica foi concedida. A Beta 8.3 protege W-07 PUT/POST e W-05 PUT, mas não demonstra que todos os writers C16 foram integrados, desabilitados ou contidos. Writers não exercitados permanecem pendentes/sem prova; a autoridade privilegiada ainda é capaz de escrita direta dentro das coleções concedidas, então a contenção depende de restringir seu processo e seus segredos.

Limitações adicionais:

* HMAC autentica e protege integridade no canal privado; não substitui TLS em transporte operacional.
* A chave API↔autoridade existe em ambos processos de teste. O harness não prova gestão/rotação de segredos fora do Docker efêmero.
* A API é gateway confiável; comprometimento total dela está fora da prova.
* Não se validou política/role/credencial MongoDB operacional nem distribuição efetiva.
* Não se validou backup/restore, resposta a incidentes, observabilidade operacional, rollback ou rollout gradual.
* O startup comum retorna 503 para as operações selecionadas sem a capacidade experimental; é fail-closed, mas a disponibilidade operacional futura depende da integração aprovada.

Matriz C16 e classificação individual: consultar [Beta 8.2 — matriz de cobertura de writers](beta8-2-writer-coverage-matrix.md). A Beta 8.3 não recontou todos os writers contra todos os arquivos do commit-base e não altera as classificações históricas sem novos testes.

## AN–AS. Gates, ADR-008, arquivos e veredito

ADR-008 permanece **BLOCKED**. Nenhum gate foi promovido. A documentação de Beta 8.2 registra G1 PARTIAL; G2 NOT_VERIFIED; G3 NOT_VERIFIED; G4 PARTIAL; G5 NOT_VERIFIED; G6 PARTIAL; G7 NOT_VERIFIED; G8 NOT_VERIFIED; G9 BLOCKED; G10 BLOCKED. Há relatórios antigos com G7 PARTIAL; essa divergência histórica foi preservada e não alterada.

Arquivos desta entrega: `backend/routes_content.py`; `backend/services/beta8_1_staging_authority.py`; `backend/services/beta8_curriculum_promotion.py`; `backend/services/beta_curriculum_staging.py`; novos `backend/services/beta8_3_*`; `backend/test_support/beta8_3_*`; `backend/unit_tests/test_beta8_3_internal_protocol.py`; `backend/integration_tests/beta8_3_process_security.py`; `ops/beta8-3-security/*`; e documentação Beta 8.3. Nenhum arquivo em `docs/courses/trilhacode/`, `docs/migracao/`, configuração operacional ou deploy foi alterado.

**A — AUTORIDADE EDITORIAL ISOLADA POR PROCESSO E CREDENCIAIS EM AMBIENTE DESCARTÁVEL**

**B — TRÊS OPERAÇÕES EDITORIAIS VALIDADAS ATRAVÉS DA AUTORIDADE SEPARADA**

**C — STAGING VALIDADO COM AUTORIDADE SEPARADA NO ESCOPO EXPERIMENTAL**

**D — REGRESSÕES PARCIALMENTE VALIDADAS — COBERTURA PENDENTE**

**GLOBAL — BETA 8.3 PARCIALMENTE VALIDADA — ISOLAMENTO, INTEGRAÇÃO OU REGRESSÕES PENDENTES**

Próximo incremento mínimo: executar a regressão Playwright da jornada real com API e autoridade separados; reconciliar todos os writers C16 por operação; testar privilégios efetivos e distribuição de segredos apenas mediante etapa operacional formalmente autorizada; concluir evidências de backup/restore, revogação, rollback, incidente e observabilidade para ADR-008. Até lá, não promover gates, publicar, homologar operacionalmente ou lançar.
