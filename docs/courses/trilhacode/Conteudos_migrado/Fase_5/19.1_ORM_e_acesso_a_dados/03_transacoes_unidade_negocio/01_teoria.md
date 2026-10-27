---
arquivo_id: "f5-19-1-03-transacoes-unidade-negocio-01-teoria"
parent_key: "19.1"
tipo_arquivo: "theory"
assunto: "03_transacoes_unidade_negocio"
ordem: 3
itens_origem: ["Microtópico 3 — Transações e unidade de negócio"]
---

## Microtópico 3 — Transações e unidade de negócio
Uma transação agrupa operações que precisam ser confirmadas ou desfeitas juntas. Delimite-a pela unidade lógica de negócio, por exemplo, registrar pedido e itens. Use o mecanismo transacional documentado pelo ORM e garanta que todas as operações que precisam de atomicidade usem a mesma transação/conexão.

Transação não substitui constraint, controle de concorrência ou idempotência. A duração e o nível de isolamento afetam bloqueios e comportamento concorrente; mantenha a transação curta e evite chamadas externas lentas dentro dela. Se uma operação combina banco e serviço externo, uma transação do banco não torna ambos atômicos.

**Exemplo:** criar uma transferência pode exigir debitar uma conta e creditar outra na mesma transação. Uma restrição de saldo e a estratégia de concorrência precisam ser consideradas para evitar que duas transferências simultâneas violem a regra.

**Erro comum:** abrir transação, chamar um serviço remoto e só então concluir o banco. A latência externa prolonga locks e o serviço não participa automaticamente do rollback.

**Checagem:** o que precisa acontecer se a segunda gravação falhar? A primeira também deve ser desfeita, pois ambas pertencem à mesma unidade atômica.

