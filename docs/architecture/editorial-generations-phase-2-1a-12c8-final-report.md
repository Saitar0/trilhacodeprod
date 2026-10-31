# Fase 2.1A.12C.8 — Relatório final

**Data da validação:** 2026-10-29 UTC
**Conclusão:** contrato transacional experimental validado no MongoDB 7 descartável; integração operacional não autorizada.

## A. Resultado executivo

Foi implementado um contrato experimental que compõe a revisão/CAS e o fencing por trilha já existentes com a atualização sintética do bloco, auditoria editorial obrigatória, histórico imutável e recibo idempotente na mesma transação MongoDB. A suíte final persistente passou em 44/44 casos, incluindo falhas antes e durante a transação, fencing, CAS, replay, resposta perdida simulada, encerramento de processo cliente e concorrência por processos, tarefas assíncronas e threads.

O teste demonstra o contrato isolado em replica set de um nó. Não demonstra compatibilidade com o schema ativo, cobertura dos escritores reais, ambiente implantado, failover multinó ou prontidão para integração. Nenhum serviço ativo foi alterado e nenhum dado real foi utilizado.

## B. Git e isolamento

| Campo | Valor |
|---|---|
| Branch | `codex/fase2-1a-12c8-editorial-transaction-protocol` |
| Worktree | `C:\Users\Joao\.codex\worktrees\trilhacode-fase2-1a-12c8-editorial-transaction-protocol\trilhacodeprod` |
| Base obrigatória | `0b3a78f028cba5d108c1c1fe6a48205bcb2ac443` |
| Commits locais de código/testes | `7cf2c9075737cb77c3b2974accfc00640a6ffa05`, `cf33b0c202e351d6d3f9485e8c17c16c798190da`, `22064624df0bc993c1067ce226d61f3114534a45` |

A worktree foi criada isoladamente com sparse-checkout. O checkout original não foi alterado. Os diretórios de curso e migração não foram materializados. Push, PR, merge, rebase e operações remotas não foram executados.

## C. Reutilização e arquitetura

O módulo [experimental_editorial_block_commit.py](../../backend/curriculum_contract/experimental_editorial_block_commit.py#L83) compõe o protocolo persistente já validado: identidade do escritor, preparação persistida, CAS de revisão da trilha, fencing, fingerprint, histórico e recibo. Não introduz revisão por bloco.

Uma extensão privada, opcional e compatível com chamadas existentes foi acrescentada ao método `commit` do adaptador para executar o participante na sessão e transação que já controlam CAS, histórico e recibo. A necessidade decorre de o adaptador ser dono dessa fronteira; copiar a lógica ou criar outro controle de revisão produziria autoridade divergente. O participante experimental atual faz somente writes determinísticos e session-bound. O adaptador usa `with_transaction`, com callback potencialmente repetido em retry transacional.

## D–I. Auditoria, CAS, fencing, idempotência e retry

* O bloco e o registro de auditoria obrigatório são escritos juntamente com o estado da trilha, histórico e recibo. A transação confirmada torna todos visíveis; falha antes do commit reverte os writes da confirmação.
* CAS confere a revisão esperada e atualiza condicionalmente revisão, fence e sequência de controle da trilha. Disputas pela mesma revisão resultam em um vencedor e conflito explícito.
* Avanço de fence altera o mesmo documento de coordenação, inclusive quando a revisão editorial não avança. A disputa entre fence e commit teve resultado serializável nos testes; handles obsoletos foram rejeitados.
* Repetição idêntica recupera o recibo sem nova alteração, revisão, auditoria ou histórico. Chave reutilizada com outra intenção é conflito. Preparação `PREPARED` não é confirmação.
* O adaptador tenta reconciliar recibo persistido em `UnknownTransactionCommitResult`; se não consegue provar o resultado, expõe `CommitOutcomeUnknown`. A falha de resposta dos testes foi simulada por fault injection após confirmação/leitura; não foi uma interrupção real de rede.

Os erros de CAS, fencing, identidade idempotente, bloco ausente, validação e resultado de commit desconhecido permanecem distinguíveis no contrato experimental. Exceções brutas do driver podem continuar existindo para falhas que não sejam mapeadas pelo protocolo; isso não define respostas HTTP.

## J. Ambiente e isolamento

| Propriedade | Evidência |
|---|---|
| Docker | Client/server `29.8.2` |
| MongoDB | `7.0.43`, imagem `mongo:7.0.43`; image ID local `sha256:1f995ad6fdb93244a1addab1b58f934a0bc2f5643c38e02f5e9d7f0c7d227a7b` (não é apresentado como digest de manifesto OCI) |
| Topologia | Replica set `rs12c8`, um membro `PRIMARY`, WiredTiger, sessões lógicas disponíveis |
| Driver/runtime | PyMongo `4.18.2`, Python `3.11.9` |
| Container desta fase | `e63a39b8aae10c895f1b142d9586e9899f261527faa5c2c01324918e4be45682`, label `io.trilhacode.phase=2.1a.12c8` |
| Rede desta fase | `trilhacode-12c8-editorial-net`, ID `13bd527f94fa00f21cfe853075c085c465d190e014d76d58d85697984b8b7a32`, bridge dedicada, masquerade de saída desativado |
| Dados/porta | Sem mounts; diretórios Mongo em tmpfs; porta apenas em `127.0.0.1:27138` |
| Banco | Um banco aleatório `editorial_revision_test_*` por caso, com marcador de propriedade e apenas conteúdo sintético |
| Concerns transacionais | `snapshot`, `primary`, `majority` com journal |

O teste verificou label, ID da imagem, mounts, tmpfs, porta, rede e pertença do container antes de conectar. Após os testes, não havia banco com o prefixo descartável. Nenhuma URI operacional foi consultada; a URI de teste foi explícita, local e sem credenciais.

`majority` nesta topologia significa confirmação pelo único membro. O teste não demonstra redundância, failover ou resistência a perda do host.

## K. Testes

| Suíte | Coletados/executados | Aprovados | Falhas | Skips |
|---|---:|---:|---:|---:|
| Contrato transacional C8 em MongoDB 7 | 44/44 | 44 | 0 | 0 |
| Repetições concorrentes C8 (T19, T27, T34; três rodadas) | 9/9 adicionais | 9 | 0 | 0 |
| Concorrência assíncrona C8 (T44, execução direcionada adicional) | 1/1 adicional | 1 | 0 | 0 |
| Regressões persistentes C3 e segurança de URI | 27/27 | 27 | 0 | 0 |
| C1, C5, C6 e contrato offline do adaptador C2 | 92/92 | 92 | 0 | 0 |
| PoC offline de gerações | 26/26 | 26 | 0 | 0 |

A suíte C8 final levou 95,269 s; as 27 regressões C3 levaram 27,608 s. Os testes C3 usaram bancos aleatórios próprios com marcadores e os descartaram; não reutilizaram bancos de outras fases. Somando as suítes distintas, foram 189 testes aprovados, sem falhas ou skips; houve dez execuções concorrentes direcionadas adicionais. T19 usa processos Python independentes e conexões próprias; T44 usa tarefas `asyncio` delegadas a threads, cada uma com seu próprio cliente MongoDB.

A suíte persistente C7 não foi executada: ela fixa identidade, porta, replica set e ownership de recursos próprios C7. Reaproveitar o servidor/banco de outra fase contrariaria o isolamento por fase. Os casos C8 exercitam a nova composição, mas não substituem uma nova execução do writer real C7.

`py_compile` passou nos módulos C8. Ruff e Mypy foram consultados, mas não estão instalados no ambiente Python disponível; não foram instalados nem declarados aprovados. Não houve testes da aplicação, Docker Compose de produto, migração ou workflow.

## L. Compatibilidade com o backend ativo

Não foi demonstrada. O experimento é síncrono, atualiza somente um título sintético, usa IDs string, collections namespaced do protocolo e uma auditoria experimental. O writer real observado na C7 é assíncrono, utiliza tipos e campos do schema ativo e chama auditoria sem sessão compartilhada. O schema operacional `edit_history`, grants reais, validações, payloads permitidos, roles e latência não foram validados. Não houve integração ou import operacional.

## M–O. Segurança, regressões e gates

Os módulos experimentais são referenciados apenas pelo harness/testes. As buscas não encontraram imports em rotas, serviços ou startup. Nenhum banco de aplicação, conteúdo real, dados de aluno, credencial operacional, Coolify, GHCR, staging ou produção foi acessado.

Estados históricos preservados, sem promoção:

| Gate | Estado mantido |
|---|---|
| G1 | `PARTIAL` |
| G2 | `NOT_VERIFIED` |
| G3 | `NOT_VERIFIED` |
| G4 | `PARTIAL` |
| G5 | `NOT_VERIFIED` |
| G6 | `PARTIAL` |
| G7 | `PARTIAL` |
| G8 | `NOT_VERIFIED` |
| G9 | `BLOCKED` |
| G10 | `BLOCKED` |

ADR-008 permanece bloqueado. A validação isolada não autoriza writers, migração, deploy ou cutover.

## P. Limpeza e limitações restantes

Os bancos aleatórios foram descartados pelo teardown após validar o marcador; a consulta final não encontrou nenhum banco com o prefixo de teste. O container exclusivo C8 foi parado e removido após validar seu ID, etiqueta, imagem, ausência de mounts e vínculo único à rede C8. A rede C8 foi removida somente depois de confirmar seu ID, etiqueta e ausência de membros. A inspeção final confirmou ambos ausentes. O venv preexistente da fase C7 não foi removido ou alterado.

Limitações centrais: replica set de nó único; sem failover; sem teste de perda de rede/commit desconhecido real; sem compatibilidade com schema ou autenticação operacionais; sem prova contra escritores que ignorem o protocolo; sem cobertura global dos writers; sem prova de retenção, grants ou cutover.

## Q–T. Arquivos, próximo incremento e veredito

Arquivos de código/teste desta fase:

* [mongodb_editorial_revision_adapter.py](../../backend/curriculum_contract/mongodb_editorial_revision_adapter.py#L556) — hook privado, opcional e limitado à sessão transacional existente.
* [experimental_editorial_block_commit.py](../../backend/curriculum_contract/experimental_editorial_block_commit.py#L1) — contrato experimental.
* [editorial_block_commit_harness.py](../../backend/integration_tests/editorial_block_commit_harness.py#L1) — falhas determinísticas e processos auxiliares de teste.
* [test_editorial_block_commit_protocol.py](../../backend/integration_tests/test_editorial_block_commit_protocol.py#L1) — 44 testes persistentes.

Documentos desta fase:

* [Contrato técnico](editorial-generations-phase-2-1a-12c8-transaction-protocol.md).
* Este relatório final.

**Próximo incremento único recomendado:** obter autorização específica para um estudo de compatibilidade não operacional que confronte o contrato sintético com os schemas reais de `content_blocks` e `edit_history`, tipos de identificadores e semântica assíncrona do writer; nenhum writer deve ser integrado até essa compatibilidade e os gates pertinentes serem aprovados.

**Veredito:** `VALIDAÇÃO PERSISTENTE ISOLADA APROVADA — INTEGRAÇÃO NÃO AUTORIZADA`.
