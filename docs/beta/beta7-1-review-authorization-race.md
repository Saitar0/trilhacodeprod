# Beta 7.1 — revogação de escopo e confirmação da correção

## Garantia experimental

A prévia implementa ponto de linearização em MongoDB: a transação de correção escreve o mesmo documento de grant cuja atualização efetua a revogação. Dentro da transação, o serviço revalida grant ativo e revisão, incrementa sua revisão como fence, aplica CAS à entrega e registra histórico/auditoria. Revogação concorrente escreve o mesmo grant. O conflito do replica set serializa a ordem sem lock em memória.

## Cenários persistentes no replica set descartável

* **Revogação confirmada antes da correção:** barreira determinística pausou a correção antes do fence; revogação foi confirmada; ao prosseguir, a transação conflitou e retornou 409. A entrega permaneceu `AWAITING_REVIEW`; não houve histórico, auditoria parcial ou progresso derivado.
* **Correção confirmada antes da revogação:** transação registrou `NEEDS_REVISION` e uma auditoria; só depois o grant foi revogado. A decisão confirmada e o registro foram preservados.

Saída do harness: `PERSISTENCE_VERIFIED`, `revocation_before_commit=review_conflicted_no_partial_write`, `commit_before_revocation=review_and_audit_preserved`, dois registros sintéticos. A mesma transação contém a decisão e a auditoria; progresso do projeto permanece não concluído e bloqueado por critério pedagógico.

## Limites

Isso fecha a janela no **grant sintético da prévia** e define revogação como efetiva no commit que serializa a atualização do grant. Não integra grants operacionais nem prova a contenção global de writers C8–C16. A operação depende de replica set e transações. Concorrência foi testada com ordem controlada e conflito persistente, não com teste de carga multi-processo. É evidência isolada, não autorização para ativar o serviço.
