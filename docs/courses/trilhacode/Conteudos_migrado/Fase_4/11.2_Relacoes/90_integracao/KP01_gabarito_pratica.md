---
arquivo_id: "f4-11-2-90-integracao-kp01-gabarito-pratica"
parent_key: "11.2"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_joins_chaves_preservacao_linhas", "03_subconsultas_existencia"]
ordem: 1
itens_origem: ["P1"]
---

**Solução de referência:**
```sql
SELECT c.id, c.nome
FROM cliente AS c
LEFT JOIN pedido AS p ON p.cliente_id = c.id
WHERE p.id IS NULL;
```
O resultado é Beto (id 2). Para manter todos os clientes e combinar apenas pedidos pagos:
```sql
SELECT c.id, p.id AS pedido_id
FROM cliente AS c
LEFT JOIN pedido AS p
  ON p.cliente_id = c.id
 AND p.status = 'pago';
```
Clientes sem pedido pago permanecem com pedido_id NULL.

