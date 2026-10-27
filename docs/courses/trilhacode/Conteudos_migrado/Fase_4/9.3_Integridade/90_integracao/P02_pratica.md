---
arquivo_id: "f4-9-3-90-integracao-p02-pratica"
parent_key: "9.3"
tipo_arquivo: "practice"
assuntos: ["01_constraints_de_coluna", "02_integridade_referencial_e_exclusao"]
ordem: 2
itens_origem: ["P2"]
---

### Atividade 2 — Integridade de pedidos e exclusão
Modele Pedido e ItemPedido. Cada item pertence a um pedido existente e a um produto existente. A combinação pedido/produto não pode se repetir. Uma linha não pode ter quantidade inferior a 1. Considere que pedidos confirmados devem ser preservados mesmo se o cliente solicitar remoção de sua conta.

**Tarefas**
1. Especifique PKs, FKs, nulabilidade, unicidade e CHECK.
2. Escolha a ação referencial ao apagar um pedido e justifique.
3. Explique por que a remoção do cliente não deve apagar pedidos confirmados em cascata.
4. Liste um INSERT válido e três violações esperadas.

**Dica:** diferencie a dependência de ItemPedido em relação a Pedido da obrigação de preservar o histórico comercial.

