# Fase 2.1A.12C.10 — Relatório final

## Resultado executivo

A fronteira editorial foi validada parcialmente, em ambiente isolado. O contrato experimental combina o role checker real `content.write` com um escopo de trilha sintético, revisões condicionais, identidade idempotente derivada por HMAC, capability criada no servidor de teste, auditoria obrigatória e adaptador nativamente assíncrono. Em MongoDB 7 descartável, foram exercitados commit/replay, rollback por falha de auditoria, CAS concorrente, fencing, resposta mínima e replay depois de remover o bloco. A execução por PyMongo síncrono em `asyncio.to_thread` também foi comparada em uma transação C8.

Isso **não** comprova IAM real, autorização por trilha, compatibilidade operacional ou cobertura dos escritores. Nenhum runtime ativo foi integrado.

**Veredito:** `FRONTEIRA EDITORIAL PARCIALMENTE VALIDADA — DECISÕES E ADAPTAÇÕES PENDENTES`.

## Git e isolamento

* Base exata: `61f58affcc55bb4e5d0648a3b1f368032211e779` (C9; parent `63c190fb1cbaba423115bb307db0f95b9c111079`).
* Branch: `codex/fase2-1a-12c10-editorial-api-iam-async`.
* Worktree: `C:\Users\Joao\.codex\worktrees\trilhacode-fase2-1a-12c10-editorial-api-iam-async\trilhacodeprod`.
* Sparse checkout configurado antes de materializar arquivos; checkout original e outras worktrees permaneceram intactos.
* Apenas arquivos experimentais novos e dois documentos Markdown estão previstos para o commit local. Sem push, PR, merge, rebase, deploy ou operação remota.
* O relatório integra o commit documental local desta fase; o hash final está no fechamento da execução.

## API atual e IAM

A rota atual é `PUT /api/blocks/{block_id}`, com `BlockUpdate`, `BlockOut`, dependência `require("content.write")` e retorno do documento atualizado. A implementação do serviço não recebe revisão esperada, chave de idempotência, capability nem fence. O writer e `audit` realizam operações independentes. Referências com linhas e análise: [contrato API/IAM/async](editorial-generations-phase-2-1a-12c10-api-iam-async-contract.md#fronteira-http-atual).

`current_user` valida JWT, sessão ativa, usuário, estado da conta, versão da sessão e e-mail. `require` verifica uma tabela de permissões por papel; não foi encontrado escopo de escrita por trilha no fluxo analisado. O harness carregou `permissions.py` real e exercitou `content.write` com principal sintético, substituindo somente a dependência de autenticação. JWT, sessão, user store, grants implantados e política por trilha não foram exercitados.

## Contrato experimental de API

O harness expõe somente dentro de testes uma rota candidata versionada `/api/v2/tracks/{track_id}/blocks/{block_id}`. Ela usa `If-Match` forte com revisão esperada, `Idempotency-Key`, schema fechado, capability de servidor e uma resposta contendo somente revisão e revisão-pai. Reutilizar a chave com intenção diferente resulta em conflito. A proposta exige nova versão da API e compatibilidade gradual; não substitui o contrato ativo.

O mapa experimental é: revisão obsoleta 412; fence/intenção conflitante 409; identificador inválido 400; autorização negada 403; bloco inexistente 404; corpo inválido 422; resultado de commit indeterminado 503; falha inesperada sanitizada 500. Autenticação 401 permanece responsabilidade do dependency ativo e não foi reproduzida com JWT real.

Campos ausentes permanecem sem alteração; `null` explícito é gravado como null; strings e objetos vazios continuam valores presentes. Status fora do conjunto atual retorna 400. Schema experimental rejeita campos desconhecidos. Patch vazio é rejeitado, diferente do writer atual, que atualiza timestamp/auditoria; a diferença está documentada como decisão futura.

## Privacidade e replay

Valores privados do patch não são copiados para o payload de intenção, histórico de revisão, recibo ou resposta: a intenção contém campos alterados e um HMAC keyed do JSON canônico. O HMAC, operation ID e segredos nunca são incluídos na resposta ou logs pelo harness. A auditoria de teste mantém ator sintético e campos estruturais.

O protocolo C8 genérico continua apto a persistir `payload_json` integral; a minimização ocorre no builder da fronteira testada e não é imposta a todo chamador. Gestão de chave, ACL/retention de `edit_history` e contratos de replay após revogação permanecem abertos.

Depois que uma operação foi confirmada, replay devolveu o recibo original mesmo após exclusão do bloco, sem nova mutação nem auditoria. O harness reavaliou `content.write` no replay e negou com 403 depois que o ator sintético passou de editor para aluno. A semântica proposta representa o resultado histórico, não o documento atual.

## Async, transações e cancelamento

Foi implementado `AsyncEditorialRevisionAdapter`, que recebe somente database de `AsyncMongoClient` explícito, usa as coleções e formatos C8, sessão/transação async, snapshot read concern, majority+journal e primary. O mesmo documento de track continua autoridade única de revisão/fence. A transação inclui credencial de writer, CAS, alteração do bloco, auditoria, histórico e recibo. A implantação paralela requer testes de conformidade contínuos e não é substituta automática do adaptador C8.

Uma falha injetada depois da atualização do bloco e antes da auditoria abortou a transação inteira; bloco, revisão, auditoria, histórico e recibo confirmado permaneceram sem alteração. Repetir a mesma preparação depois de resolver a falha confirmou uma vez. Duas conexões async independentes disputando revisão 0 produziram um commit e um conflito. Um fence antigo foi rejeitado depois de avançar a autoridade sem nova revisão.

Cancelar durante um callback pré-commit propagou `CancelledError`; naquele ponto observado, o estado persistido permaneceu inalterado. Não houve cancelamento durante commit, queda real de rede, encerramento abrupto de cliente ou failover. Resultado incerto exige reconciliação da mesma identidade; não se promete rollback após confirmação.

Ponte via thread C8 e adapter async nativo foram comparados em commits sintéticos persistentes, separados por trilha/namespace, com mesmo formato básico de recibo/auditoria. O heartbeat manteve o event loop vivo durante o trabalho `to_thread`. Não foi executado benchmark útil de latência ou throughput; nenhuma conclusão de desempenho é feita.

## Testes e qualidade

MongoDB C10 foi verificado antes de fixtures: imagem local oficial `mongo:7.0.43`, image ID `sha256:1f995ad6fdb93244a1addab1b58f934a0bc2f5643c38e02f5e9d7f0c7d227a7b`, replica set `rsC10` de nó único, WiredTiger, sessões lógicas, primário, porta `127.0.0.1:29130`, tmpfs sem mounts. PyMongo `4.18.2`, Python `3.11.9`. URI de teste foi definida explicitamente no processo de teste, sem credenciais e sem `.env`.

* Testes C10: **11 passed**, sem falhas ou skips (5 unitários e 6 testes persistentes de integração).
* Repetição do cenário de CAS com dois clientes independentes: cinco execuções adicionais passaram. Uma falha anterior foi causada pelo teste usar a coleção do cliente A com a sessão do cliente B; o fake foi corrigido para associar sessão e coleção ao mesmo cliente. Não alterou o adaptador nem a aplicação.
* Regressões offline C1/C2/C5/C6/PoC: **118 passed, 38 subtests passed**.
* Total incluindo C10: **129 passed, 38 subtests passed**.
* Ruff: aprovado nos seis arquivos Python novos.
* Mypy: aprovado nos dois módulos experimentais de contrato/adaptador.
* Compilação sintática e `git diff --check`: registrados após validação final.
* C7/C8/C9 persistentes não foram reexecutados, pois suas fixtures exigem recursos/portas próprios; não reutilizei ambientes anteriores. C9 regressões persistentes não são requisito para validar o banco C10. Nenhum skip foi contado como aprovação.

## Segurança e limites operacionais

* Nenhuma rota, serviço, writer, schema operacional, IAM operacional, startup, configuração ou dependência de produção foi alterada.
* Nenhum módulo ativo importa a implementação C10; não houve conexão no import.
* Banco e fixtures continham apenas identidades/dados sintéticos. Nenhum conteúdo real foi usado.
* Nenhum acesso a `.env`, staging, produção, Coolify, GHCR ou serviço externo.
* A aplicação ativa continua usando seu contrato anterior. O harness não cria endpoint ativo nem habilita feature flag.
* A topologia local de nó único não prova failover multinó nem durabilidade de produção.
* O contêiner `trilhacode-12c10-mongo`, a rede dedicada `trilhacode-12c10-editorial-net` e o venv temporário da fase foram removidos após verificar que não restavam bancos `editorial_revision_test_c10_*`; nenhum volume persistente foi criado.

## Gates e decisões pendentes

G1 `PARTIAL`; G2 `NOT_VERIFIED`; G3 `NOT_VERIFIED`; G4 `PARTIAL`; G5 `NOT_VERIFIED`; G6 `PARTIAL`; G7 `PARTIAL`; G8 `NOT_VERIFIED`; G9 `BLOCKED`; G10 `BLOCKED`. ADR-008 continua bloqueado. A C10 não modifica a matriz nem promove gates.

Pendências mínimas: regra de escopo IAM por trilha; forma compatível da API/rollout; retenção de chaves e recibos; política de replay e revogação; gestão de segredos HMAC e acesso/retention de auditoria; escolha da estratégia async/thread; compatibilidade do schema, grants, índices e runtime implantados.

## Arquivos novos

* `backend/curriculum_contract/experimental_editorial_api_contract.py`
* `backend/curriculum_contract/experimental_async_editorial_adapter.py`
* `backend/integration_tests/editorial_api_iam_harness.py`
* `backend/integration_tests/test_editorial_api_iam.py`
* `backend/integration_tests/test_async_editorial_adapter.py`
* `backend/unit_tests/test_experimental_editorial_api_contract.py`
* `docs/architecture/editorial-generations-phase-2-1a-12c10-api-iam-async-contract.md`
* `docs/architecture/editorial-generations-phase-2-1a-12c10-final-report.md`

## Próximo incremento recomendado

O menor próximo passo seguro é deliberar e especificar a autorização de escrita por trilha e seu ponto de decisão server-side, incluindo comportamento de replay. Sem essa política, não é possível converter `content.write` por papel em capability editorial confiável para qualquer trilha. Não iniciar integração operacional antes de nova autorização específica e gates aplicáveis.

## Veredito

`FRONTEIRA EDITORIAL PARCIALMENTE VALIDADA — DECISÕES E ADAPTAÇÕES PENDENTES`.

Esta fase validou comportamento experimental em ambiente descartável. Não autorizou nem executou integração, migração, cutover, deployment ou mudança de dados operacionais.

A worktree foi verificada limpa após o commit local.
