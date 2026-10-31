# Fase 2.1A.12C.7 — Relatório final

## A. Resultado

Foi executado o `update_block` real contra MongoDB 7 descartável e verificado o estado persistido quando a auditoria falha. O writer não compartilha sessão ou transação com `audit`: uma falha de auditoria pode ocorrer depois da alteração do bloco. A proposta transacional isolada demonstrou rollback conjunto e confirmação conjunta em MongoDB.

**Veredito:** `ATOMICIDADE DE BLOCO E AUDITORIA VALIDADA EM AMBIENTE ISOLADO — INTEGRAÇÃO NÃO AUTORIZADA`.

## B. Git e isolamento

- Base exata: `2f3b60b8d40413a6beeda4785b0cdacb84c83983`; parent: `4de47162e425d82ba084c0bddeb2086d1427dec5`.
- Branch: `codex/fase2-1a-12c7-update-block-atomicity`.
- Worktree: `C:\Users\Joao\.codex\worktrees\trilhacode-fase2-1a-12c7-update-block-atomicity\trilhacodeprod`.
- Criada com `git worktree add --no-checkout`, sparse-checkout antes da materialização.
- Checkout original e demais worktrees não foram alterados. `docs/courses/trilhacode/` e `docs/migracao/` não foram materializados.
- Nenhuma operação Git remota foi executada.

## C. Escritor e política da auditoria

`update_block` em [`backend/services/blocks.py`](../../backend/services/blocks.py#L38-L45) atualiza `content_blocks`, aguarda `audit` e depois lê o documento. [`backend/audit.py`](../../backend/audit.py#L7-L11) insere separadamente em `edit_history` sem sessão explícita. Não há transação, CAS de revisão, verificação de `matched_count` ou chave de idempotência no caminho observado. A rota exige `content.write` em [`routes_content.py`](../../backend/routes_content.py#L166-L168).

O código faz a auditoria obrigatória para que a função retorne normalmente e propaga a falha, mas não define explicitamente se isso é uma obrigação de negócio transacional. Essa política continua pendente de aprovação humana.

## D. Ambiente MongoDB e isolamento

- MongoDB `7.0.43`, image ID `sha256:1f995ad6fdb93244a1addab1b58f934a0bc2f5643c38e02f5e9d7f0c7d227a7b`.
- Replica set `rs12c7`, um primary, WiredTiger e sessões lógicas habilitadas.
- PyMongo Async `4.18.2`; Python `3.11.9` em venv temporário.
- Dados em `tmpfs`; sem volumes persistentes ou mounts de host. Porta `52926` exposta apenas em loopback. Rede Docker etiquetada desta fase com masquerade desativado.
- Cada caso criou banco `editorial_block_audit_test_*` com marcador de execução, validado antes de escrita e antes do descarte. Ao final, nenhum banco com esse prefixo permaneceu.
- Os testes conectaram somente ao endpoint loopback do contêiner e não acessaram bancos preexistentes, produção, staging, Docker alheio, dados reais ou endpoints externos. PyMongo foi instalado em venv temporário isolado, sem alterar o Python global.
- O contêiner e a rede desta fase foram removidos; os volumes anônimos da primeira tentativa também foram confirmados ausentes. O venv temporário criado em `C:\Users\Joao\AppData\Local\Temp\trilhacode-12c7-venv` permanece. A tentativa de remoção recursiva foi bloqueada pela política local de execução; nenhum arquivo fora desse venv foi alvo da limpeza.

`w: "majority"` na proposta transacional foi testado em um replica set de um único nó e, portanto, corresponde a uma confirmação de um membro; não demonstra failover ou tolerância a falhas multinó.

## E. Cenários e resultados persistentes

- **22/22 testes MongoDB passaram em duas execuções finais** (18,815 s e 18,772 s), sem skips.
- No writer atual, falha antes do update deixou ambos inalterados; rejeição real do validador Mongo também não alterou o bloco.
- Após `update_one` retornar com sucesso e antes da auditoria, o erro injetado deixou o bloco modificado e zero linhas de auditoria.
- Uma falha no insert de auditoria teve o mesmo estado parcial e foi propagada.
- Se o insert foi concluído e o erro foi injetado depois, bloco e auditoria permaneceram apesar do erro ao chamador.
- Falha na leitura de retorno após auditoria também deixou ambas as escritas persistidas.
- Repetir após erro de auditoria executou novamente o update; repetir após insert confirmado sem resposta criou duas linhas de auditoria.
- Duas chamadas concorrentes do writer atual tiveram sucesso e gravaram duas auditorias; uma sobrescreveu o campo alterado pela outra.
- Na proposta transacional, sucesso confirmou bloco e auditoria juntos. Falha anterior ao insert e falha injetada depois de um insert dentro da transação abortaram ambos. Duas transações concorrentes para a mesma revisão tiveram um vencedor e um conflito, sem retry de domínio.

Uma primeira execução da suíte experimental encontrou erros no próprio código de teste: uso incorreto da API de sessão Async PyMongo e índice único não parcial para registros legados sem `operation_id`. Ambos foram corrigidos nos arquivos novos, sem alterar o writer; depois disso a suíte final passou duas vezes. Nenhum defeito funcional foi corrigido na aplicação.

As falhas após confirmação foram injetadas pelo proxy do harness logo após chamadas reais retornarem; não representam um corte de rede real. A resposta perdida do chamador também foi simulada após o retorno do serviço. O teste transacional de concorrência usou tarefas assíncronas concorrentes, não processos separados.

## F. Regressões e qualidade

- Regressões C6 + C5 + C1: **84/84 aprovadas**, sem skips.
- Ruff: verificação e formatação aprovadas nos três arquivos de código novos.
- Mypy: aprovado nos três arquivos com `--ignore-missing-imports --follow-imports=skip`.
- AST sintático: aprovado.
- `git diff --check`: aprovado antes da documentação; repetido na validação final.
- Não foram executados testes da aplicação completa, workflows ou testes de MongoDB em topologia diferente.

## G. Código experimental e integração

O harness carrega os fontes reais de `blocks.py`, `audit.py` e `services/common.py` sem importar `backend/database.py`, que cria `AsyncMongoClient` ao importar. O módulo transacional em `backend/curriculum_contract/experimental_block_audit_transaction.py` é independente, não é importado pelo runtime e usa somente o banco recebido pelo teste.

Busca estática confirmou ausência de imports do módulo experimental ou harness em rotas, `services/blocks.py`, servidor e serviços ativos. Nenhuma rota, writer, serviço, configuração, schema operacional, migração ou coleção real foi alterada.

## H. Gates e limitações

Gates históricos preservados: G1 `PARTIAL`; G2 `NOT_VERIFIED`; G3 `NOT_VERIFIED`; G4 `PARTIAL`; G5 `NOT_VERIFIED`; G6 `PARTIAL`; G7 `PARTIAL`; G8 `NOT_VERIFIED`; G9 `BLOCKED`; G10 `BLOCKED`. Um único writer e uma proposta experimental não comprovam cobertura de todos os escritores, compatibilidade operacional, baseline, segurança de produção ou adoção do CAS/fencing globais.

Limitações adicionais: resultado de commit ambíguo real não foi injetado; auditoria fora do mesmo MongoDB não seria atomicamente coberta; o campo `editorial_revision` e o índice parcial por `operation_id` são exclusivos da proposta sintética e não foram aprovados como schema de produção; replay de recibo idempotente não está implementado.

## I. Arquivos e commits

Arquivos novos:

- `backend/curriculum_contract/experimental_block_audit_transaction.py`
- `backend/integration_tests/editorial_block_atomicity_harness.py`
- `backend/integration_tests/test_editorial_block_atomicity.py`
- `docs/architecture/editorial-generations-phase-2-1a-12c7-block-audit-atomicity.md`
- `docs/architecture/editorial-generations-phase-2-1a-12c7-final-report.md`

O commit local será `test(curriculum): validate isolated block audit atomicity`. Não haverá push, PR, merge, rebase ou deploy; a worktree será verificada limpa depois do commit.

## J. Próximo incremento e conclusão

Antes de qualquer integração, o menor passo é uma decisão humana explícita sobre se a auditoria de `update_block` é obrigatória na mesma confirmação editorial e qual contrato de idempotência deve reger retries. Uma implementação futura exigirá nova autorização, integração com o CAS/fencing aprovado e verificação do baseline operacional; esta fase não a autoriza.
