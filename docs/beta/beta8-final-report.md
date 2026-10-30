# Trilha Code — Beta 8 — Relatório final

## A. Resultado executivo

A Beta 8 implementa e testa uma fatia isolada que une grants C12, revisão/CAS/fencing C8/C10, privilégios MongoDB restritos e uma promoção exclusivamente sintética para coleções experimentais. O servidor MongoDB negou escritas diretas dos papéis de runtime e preparação. A operação editorial sintética autorizada confirmou com recibo/histórico/auditoria; revogação ordenada antes da transação, fence obsoleto, retries e concorrência foram exercitados.

Isso não contém globalmente os 17 writers C13 nem integra C12 ao IAM ativo. O papel Mongo de autoridade ainda pode escrever diretamente nas coleções que precisa coordenar. A promoção não consome staging real nem publica. Resultado global: **BETA 8 PARCIALMENTE VALIDADA — IAM, WRITERS OU ENFORCEMENT PENDENTES**.

## B. Git e isolamento

* Base validada: `47a48c71832776b1191cb2c022054eb1712a4759`, com entregáveis Beta 7.2.
* Branch: `codex/beta8-iam-editorial-enforcement`.
* Worktree exclusiva: `C:\Users\Joao\.codex\worktrees\trilhacode-beta8-editorial-security\trilhacodeprod`.
* Nenhum commit de origem foi reescrito; sem push, PR, merge, pull, cherry-pick, rebase ou deploy.
* Worktrees existentes foram listadas em modo de inspeção. O checkout original tem alterações locais não relacionadas; não foi tocado. Branch Beta 7.2 permaneceu intacta.
* Commit local de implementação/harness: `9de52aac`; o commit documental final está no `git log` desta branch. Não houve alteração de referência remota.

## C. Arquitetura do IAM

O runtime versionado valida JWT em cookie ou Bearer, sessão em `auth_sessions`, usuário ativo em `users`, `token_version` e `email_verified` (`backend/security.py::current_user`). `backend/permissions.py::require` deriva permissões globais de papéis estáticos em `backend/constants.py`; a dependência ativa não consulta grants C12 por trilha. `admin`/`editor` incluem `content.write` global no código atual.

C11/C12 fornece contrato experimental separado de principal, sessão e grant por trilha. Beta 8 reutiliza essa autoridade, sem criar uma nova autenticação ativa. Porém, seus atores sintéticos não são JWTs do runtime; a ponte entre `current_user` e C12 segue pendente. Não foi alegada integração operacional.

## D. Grants e autorização

A ação sintética de edição exige principal ativo com `content.write`, sessão ativa/não expirada, grant ativo exato para `block.update` e track resolvido pelo documento de bloco. A promoção exige `content.publish` e grant da trilha. Papel sem escopo, sessão inválida, grant ausente/revogado ou payload fora da fronteira resulta em negação. IDs e estados de cliente não atribuem escopo.

A matriz completa e os estados verificados estão em `beta8-resource-authorization-matrix.md` e `beta8-iam-inventory.md`. O papel nominal admin não recebe escopo C12 por padrão: o contrato C12 exige grant global explícito `track_id="*"` e marcador próprio.

## E. Revogação e autorização transacional

O teste persistente pausa a operação depois da autorização de requisição e antes de iniciar a transação. A revogação do grant confirma; ao liberar a operação, a condição C12 dentro da transação não encontra grant ativo/epoch esperado, aborta o commit e mantém conteúdo/revisão intactos. O ponto de ordem provado na fatia é o commit MongoDB que agrega fatos C12, mutação participante, CAS, fence, histórico, recibo e auditoria.

Uma disputa real entre duas mutações também confirmou um vencedor e um `RevisionConflict`. O cenário de revogação por barreira não é uma corrida de scheduler com duas transações simultaneamente abertas. Revogação do IAM ativo, epoch de política global, propagação multi-instância e drenagem de processos legados não foram provados. Detalhes em `beta8-grant-revocation-consistency.md`.

## F. Auditoria de autorização

Decisões negadas gravam ação, ator, recurso, operação, código fechado de motivo e versão do schema, sem token, senha, segredo ou conteúdo de submissão. Eventos de commit e promoção são inseridos dentro da transação C8/C10. A escrita de negação é best-effort; falha de logging nunca converte DENY em ALLOW. A identidade experimental de writer não tem permissão de leitura das coleções de auditoria.

## G. Entrega A — veredito IAM

**IAM PARCIALMENTE VALIDADO — GRANTS OU REVOGAÇÃO PENDENTES**.

Validado experimentalmente: grants de trilha, sessão, permissão, revalidação transacional e ordering de revogação C12/C10. Pendente: integrar principal e sessão ao JWT/IAM ativo sem segunda fonte de identidade; política/epoch operacional; grants reais, delegação e revogação no processo implantado; HTTP e configuração efetiva.

## H. Writers e modelo de ameaças

A lista C13 atual foi comparada aos arquivos/símbolos: W-01–W-17 permanecem localizáveis, W-17 sendo classe. Os 17 permanecem `runtime=NOT_VERIFIED`; nenhum writer legado foi alterado ou executado. O C16 já provou que `readWrite` direto contorna CAS/fence/auditoria.

Controles relevantes incluem CRUD de trilhas/nós/blocos/relações, catálogo global, importação, publicação, snapshots, restauração, seed, migrações, histórico e PoC de gerações. Os riscos de maior impacto continuam em W-02/W-04/W-06/W-10/W-11 e W-16. Matriz reconciliada em `beta8-editorial-writer-inventory.md`; sequência gradual em `beta8-writer-integration-plan.md`.

## I. Matriz MongoDB e provas de negação

Em MongoDB 7 descartável foram criadas identidades sintéticas distintas:

* `beta8-runtime`: leitura de coleções sintéticas; update em `content_blocks` e insert em `activity_publications` foram rejeitados pelo MongoDB.
* `beta8-preparer`: somente staging experimental; update de bloco e insert de head foram rejeitados pelo MongoDB.
* `beta8-editorial-authority`: acesso necessário a C8/C10/C12, bloco sintético e coleções Beta 8; sem privilégio de escrita em coleções operacionais de publicação.
* `beta8-root`: bootstrap e cleanup do harness efêmero; credencial não foi usada pelos clientes runtime/preparation/editorial.
* Auditoria separada é proposta, não uma identidade exercitada.

MongoDB aplica privilégio por coleção, não por documento/operação Python. Qualquer processo com a credencial de autoridade pode escrever diretamente em `content_blocks` e nos registros C8/C12. A fatia demonstra redução de privilégios para processos comuns, não contenção global nem isolamento do próprio processo confiável de autoridade. Consulte `beta8-mongodb-least-privilege.md` e `beta8-editorial-enforcement-proof.md`.

## J. Autoridade editorial, CAS, fencing e idempotência

Uma atualização limitada de título/corpo em bloco sintético `draft` segue C12 → prepare C10 → CAS/fence e participante transacional. O teste observou mutação autorizada, histórico C8, auditoria, retry do mesmo operation ID sem duplicação, grant revogado entre autorização de requisição e commit, duas edições concorrentes com um conflito e writer preparado com fence obsoleto rejeitado. O role da autoridade permanece uma fronteira de confiança de serviço.

## K. Preservação do histórico do aluno

A role de autoridade B8 não possui privilégios em `progress`, `activity_attempts` e `submissions`; runtime e preparador também não. O harness confirmou que as coleções operacionais de aprendizagem/publicação não foram criadas. Gerações experimentais anteriores são append-only e preservadas.

Isso não valida W-02/W-06/W-11 nem outros caminhos operacionais de exclusão/restauração. Atomicidade não substitui política de retenção. Evidência e limite em `beta8-student-history-preservation.md`.

## L. Staging e contrato de promoção

O contrato tipado exige ID/track sintéticos, hash canônico, versão, estado VALIDATED, approval marcado `SYNTHETIC_FIXTURE_APPROVED`, alvo fixo `beta8_experimental` e preservação de gerações anteriores. O schema dos registros sintéticos rejeita metadados desconhecidos. O serviço grava geração, head CAS, auditoria e recibo em coleções exclusivas, sem importar staging Beta 5 nem criar rota.

Não foi implementado adaptador que leia ou confirme um lote real das coleções Beta 5; o campo VALIDATED é uma precondição do candidato sintético, não prova de validação de staging. A primeira fase real, uma rubrica PROPOSED, ou qualquer documento operacional não pode ser promovido por esse contrato.

## M. Concorrência, retry e recuperação da promoção

No namespace sintético: promoção inicial e replay idempotente, identidade divergente conflitante, grant ausente negado, duas promoções sobre a mesma revisão/head com um vencedor e um conflito, e preservação da geração anterior. Falha transacional aborta os participantes no MongoDB usado; perda natural de processo após todos os pontos de commit não foi ensaiada. Não se afirma recovery operacional. Resultados em `beta8-promotion-concurrency-results.md`.

## N. Entrega B — veredito writers

**CONTENÇÃO EDITORIAL PARCIALMENTE VALIDADA — WRITERS OU PERMISSÕES PENDENTES**.

Validado: MongoDB rejeita os writes dos papéis runtime e preparador; um serviço representativo segue grants/CAS/fence/auditoria. Pendente: retirar ou restringir todas as credenciais dos 17 caminhos, isolar processo de autoridade, provar privilégios efetivos e conter importação, publicação, restauração, exclusão, migrações e scripts reais. Nenhuma contenção global é declarada.

## O. Entrega C — veredito promoção

**PROMOÇÃO CURRICULAR EXPERIMENTAL VALIDADA — ATIVAÇÃO NÃO AUTORIZADA**.

Válida somente para a transição sintética entre candidate validado sintético e geração em `_beta8_experimental_*`, com grant, revisão, fence, auditoria, CAS, replay e conflito testados. Não é integração de staging, publicação, aprovação editorial ou autorização de lançamento.

## P. Ambiente, isolamento e limpeza

Última prova: execução `bb47c868` no Docker Desktop `desktop-linux`, MongoDB 7.0.43 em replica set, rede Docker `internal` exclusiva, sem portas publicadas nem volumes; `data/db`, `data/configdb` e chave Mongo ficaram em tmpfs/segredo temporário. O harness recebeu URI apenas do Compose e exigiu IDs completos, labels, imagem esperada, rede, mount, tmpfs, marcador do DB e senha aleatória. Gate passou antes da primeira escrita.

Ao terminar, o marcador foi revalidado; DB e contêiner foram removidos, rede removida, imagem Beta 8 removida por label/ID verificados e chave temporária apagada. A execução não usou `localhost:27017`, nem tocou a instância citada na Beta 4. Não foi usado banco operacional.

## Q. Testes e qualidade

* Pytest direcionado: **74 passed** em seis módulos offline escolhidos. Módulo Beta 8: **11 passed**.
* Harness persistente: todas as cinco linhas PASS: gate, negação por role Mongo, autoridade C8/C10/C12, promoção sintética e concorrência/revogação/fence.
* Ruff: passed nos cinco arquivos Python Beta 8.
* MyPy: passed individualmente nos quatro módulos novos de contrato/serviço/harness.
* `py_compile`: passed nos cinco arquivos Python Beta 8.
* PowerShell parser: passed.
* `docker compose config --quiet`: passed com valores sintéticos; script repetiu o contrato durante a prova persistente.
* Validação JSON dos inventários C13, grants C13 e contrato C15: passed.
* Varredura de links relativos: nenhum link relativo não verificado. Varredura de padrões de segredos: passed. `git diff --cached --check`: passed antes do commit.
* Suíte completa pytest, regressões persistentes históricas, HTTP e frontend: not run.

Detalhes: `beta8-regression-results.md`.

## R. Entrega D — veredito de verificação

**VERIFICAÇÃO DE SEGURANÇA PARCIAL — EVIDÊNCIAS PENDENTES**.

A fatia isolada foi testada offline e com persistência. HTTP B8, integração ao JWT ativo, suites persistentes históricas e cobertura de writers reais não foram demonstrados.

## S. ADR-008 e gates

ADR-008 permanece **BLOCKED**. Os estados históricos permanecem exatamente: G1 PARTIAL; G2 NOT_VERIFIED; G3 NOT_VERIFIED; G4 PARTIAL; G5 NOT_VERIFIED; G6 PARTIAL; G7 PARTIAL; G8 NOT_VERIFIED; G9 BLOCKED; G10 BLOCKED. Nenhum gate foi promovido.

Pendências de evidência de runtime, credenciais/roles, topologia, política e grants, containment, leitores/gerações, preservação de dados, backup/restore/rollback, incidente, auditoria e rollout estão em `beta8-adr008-evidence-gaps.md`.

## T. Arquivos Beta 8

### Backend

* `backend/curriculum_contract/beta8_promotion_contract.py`
* `backend/services/beta8_editorial_enforcement.py`
* `backend/services/beta8_curriculum_promotion.py`
* `backend/unit_tests/test_beta8_security_contracts.py`
* `backend/integration_tests/beta8_security_persistence.py`

### Harness

* `ops/beta8-security/compose.yaml`
* `ops/beta8-security/Dockerfile`
* `ops/beta8-security/Dockerfile.dockerignore`
* `ops/beta8-security/requirements.lock`
* `ops/beta8-security/run-local.ps1`

### Documentação

* `docs/beta/beta8-adr008-evidence-gaps.md`
* `docs/beta/beta8-curricular-promotion-contract.md`
* `docs/beta/beta8-editorial-enforcement-proof.md`
* `docs/beta/beta8-editorial-writer-inventory.md`
* `docs/beta/beta8-grant-revocation-consistency.md`
* `docs/beta/beta8-iam-inventory.md`
* `docs/beta/beta8-mongodb-least-privilege.md`
* `docs/beta/beta8-promotion-concurrency-results.md`
* `docs/beta/beta8-resource-authorization-matrix.md`
* `docs/beta/beta8-regression-results.md`
* `docs/beta/beta8-student-history-preservation.md`
* `docs/beta/beta8-writer-integration-plan.md`
* `docs/beta/beta8-final-report.md`

## U. Próxima decisão e incremento mínimo

Antes de qualquer homologação: aprovar fonte de identidade única para grants; definir epoch/política de revogação com ponto de commit; provisionar autoridade como processo isolado e retirar write direto dos runtimes; reconciliar privilégios operacionais por evidência autorizada; migrar um writer real de baixo impacto com chamada HTTP e prova negativa de credenciais antigas; validar auditoria, backup, rollback e preservação de alunos; então reavaliar ADR-008. Não usar esta fase para acessar ambientes reais.

## V. Veredito global

**BETA 8 PARCIALMENTE VALIDADA — IAM, WRITERS OU ENFORCEMENT PENDENTES**.

Nenhum veredito desta fase autoriza publicação, promoção de conteúdo real, merge, push, deploy ou lançamento.

## Índice do relatório obrigatório A–AJ

| Item | Conteúdo neste relatório |
|---|---|
| A | Resultado executivo |
| B | Git e isolamento |
| C | Arquitetura do IAM |
| D | Grants e autorização |
| E | Revogação |
| F | Autorização transacional e ponto de commit |
| G | Auditoria IAM |
| H | Veredito da Entrega A |
| I | Inventário dos writers |
| J | Modelo de ameaças e bypass |
| K | Matriz de privilégios MongoDB |
| L | Provas de negação pelo banco |
| M | Autoridade editorial representativa |
| N | CAS e fencing |
| O | Idempotência |
| P | Histórico dos alunos |
| Q | Writers restantes e plano gradual |
| R | Veredito da Entrega B |
| S | Staging e contrato |
| T | Promoção experimental |
| U | Concorrência da promoção |
| V | Gerações anteriores e versões |
| W | Recuperação e cenários de falha |
| X | Veredito da Entrega C |
| Y | Ambiente descartável |
| Z | Testes e resultados |
| AA | Regressões executadas e não executadas |
| AB | Qualidade e ferramentas |
| AC | Limpeza de recursos |
| AD | ADR-008 e evidências pendentes |
| AE | Gates históricos |
| AF | Lista completa de arquivos |
| AG | Limitações não demonstradas |
| AH | Próximas decisões de homologação |
| AI | Veredito da Entrega D |
| AJ | Veredito global |

Os itens V, W e as categorias agregadas no corpo são detalhados aqui para manter a rastreabilidade do formato solicitado. Gerações antigas permanecem append-only no experimento; o recovery limita-se a transações abortadas e recursos sintéticos efetivamente ensaiados; não houve ensaio de falha natural de processo após commit.
