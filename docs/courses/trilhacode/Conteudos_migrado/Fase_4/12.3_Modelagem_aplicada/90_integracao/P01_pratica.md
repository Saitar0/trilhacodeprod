---
arquivo_id: "f4-12-3-90-integracao-p01-pratica"
parent_key: "12.3"
tipo_arquivo: "practice"
assuntos: ["01_modelo_vendas_historico", "02_invariantes_constraints_transacoes"]
ordem: 1
itens_origem: ["P1"]
---

## Práticas

### Atividade 1 — Derive um modelo a partir das regras
Uma loja vende variantes de produtos. Cada pedido pertence a um cliente e pode começar como rascunho. Um pedido confirmado precisa ter pelo menos um item. Cada item preserva a quantidade e o preço acordado. O mesmo produto pode aparecer em linhas separadas por causa de personalizações. Uma cobrança pode ser tentada mais de uma vez.

**Tarefas**
1. Liste entidades e associações.
2. Descreva cardinalidades e opcionalidades para Cliente/Pedido, Pedido/Item, Produto/Item e Pedido/TentativaPagamento.
3. Escolha uma chave para ItemPedido e justifique.
4. Identifique dois fatos históricos que não devem depender do estado atual do catálogo.

**Dica:** indique quando cada relação passa de opcional para obrigatória ao longo do ciclo do pedido.

