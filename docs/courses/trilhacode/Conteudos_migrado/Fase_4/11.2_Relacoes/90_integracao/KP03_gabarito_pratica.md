---
arquivo_id: "f4-11-2-90-integracao-kp03-gabarito-pratica"
parent_key: "11.2"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_joins_chaves_preservacao_linhas", "03_subconsultas_existencia"]
ordem: 3
itens_origem: ["P3"]
---

**Solução de referência:**
```sql
SELECT c.id, c.nome
FROM cliente AS c
WHERE EXISTS (
  SELECT 1
  FROM pedido AS p
  WHERE p.cliente_id = c.id
    AND p.status = 'pago'
);
```
A versão com JOIN:
```sql
SELECT c.id, c.nome
FROM cliente AS c
JOIN pedido AS p ON p.cliente_id = c.id
WHERE p.status = 'pago';
```
Um cliente com dois pedidos pagos aparece duas vezes na versão JOIN, uma por pedido; EXISTS retorna uma linha por cliente. Para decidir desempenho real, avalie dados, índices e plano de execução, além de preservar a semântica desejada.

