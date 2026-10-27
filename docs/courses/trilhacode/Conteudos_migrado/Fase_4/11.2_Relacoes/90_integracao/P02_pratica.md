---
arquivo_id: "f4-11-2-90-integracao-p02-pratica"
parent_key: "11.2"
tipo_arquivo: "practice"
assuntos: ["01_joins_chaves_preservacao_linhas", "02_cardinalidade_agregacoes"]
ordem: 2
itens_origem: ["P2"]
---

### Atividade 2 — Calcule gasto sem multiplicar valores
Considere Pedido(id, cliente_id, status) e ItemPedido(pedido_id, quantidade, preco_unitario). Pedido 20 é pago e possui linhas (20, 2, 15) e (20, 1, 10); Pedido 21 é pago e possui (21, 1, 40). Pedido 22 está aberto e possui (22, 3, 20).

**Tarefas**
1. Escreva a receita total dos pedidos pagos.
2. Escreva o gasto por cliente e mantenha somente clientes com gasto pago de pelo menos 30.
3. Explique por que somar um total de pedido repetido em cada linha poderia inflar o resultado.

**Dica:** calcule valor por item como quantidade × preço unitário e filtre status antes de agrupar.

