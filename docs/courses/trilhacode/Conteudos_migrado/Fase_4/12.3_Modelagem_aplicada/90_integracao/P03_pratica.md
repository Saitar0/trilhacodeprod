---
arquivo_id: "f4-12-3-90-integracao-p03-pratica"
parent_key: "12.3"
tipo_arquivo: "practice"
assuntos: ["02_invariantes_constraints_transacoes", "03_pagamentos_idempotencia", "04_consultas_sem_multiplicacao"]
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — Integre estoque e relatório sem duplicação
Uma reserva precisa reduzir o saldo disponível e gravar o item do pedido na mesma transação. Um pedido pode ter várias linhas e várias tentativas de pagamento. Defina como reservar uma unidade com segurança e escreva o relatório mensal de receita baseado nos pedidos pagos sem somar itens repetidos pelas tentativas.

**Tarefas**
1. Descreva a transação para reservar o estoque e gravar o item.
2. Defina o que fazer se a atualização condicional não retornar linha.
3. Escreva uma consulta que agregue o total de itens por pedido e depois some pedidos pagos por mês.
4. Explique como o relatório mudaria se receita significar valor capturado, incluindo reembolsos.
5. Registre duas invariantes e como verificá-las.

**Dica:** mantenha a agregação dos itens independente das tentativas de pagamento.

