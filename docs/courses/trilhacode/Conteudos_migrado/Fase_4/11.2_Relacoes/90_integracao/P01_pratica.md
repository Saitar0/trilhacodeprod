---
arquivo_id: "f4-11-2-90-integracao-p01-pratica"
parent_key: "11.2"
tipo_arquivo: "practice"
assuntos: ["01_joins_chaves_preservacao_linhas", "03_subconsultas_existencia"]
ordem: 1
itens_origem: ["P1"]
---

## Práticas

### Atividade 1 — Encontre clientes sem pedidos
Considere Cliente(id, nome) com as linhas (1, Ana), (2, Beto), (3, Caio) e Pedido(id, cliente_id) com as linhas (10, 1), (11, 1), (12, 3).

**Tarefas**
1. Escreva uma consulta que liste clientes sem pedidos.
2. Preveja exatamente os ids retornados.
3. Adapte a consulta para listar todos os clientes e somente os pedidos pagos, sem remover quem não tem pedido pago.

**Dica:** use a PK do lado direito para detectar ausência; preserve a condição de status dentro de ON na segunda consulta.

