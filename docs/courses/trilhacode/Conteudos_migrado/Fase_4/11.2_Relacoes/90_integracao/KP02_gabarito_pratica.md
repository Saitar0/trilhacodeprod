---
arquivo_id: "f4-11-2-90-integracao-kp02-gabarito-pratica"
parent_key: "11.2"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_joins_chaves_preservacao_linhas", "02_cardinalidade_agregacoes"]
ordem: 2
itens_origem: ["P2"]
---

**Solução de referência:**
```sql
SELECT SUM(i.quantidade * i.preco_unitario) AS receita
FROM pedido AS p
JOIN item_pedido AS i ON i.pedido_id = p.id
WHERE p.status = 'pago';
```
Receita = 80: pedido 20 soma 40 e pedido 21 soma 40; pedido 22 é excluído. Por cliente:
```sql
SELECT p.cliente_id, SUM(i.quantidade * i.preco_unitario) AS gasto
FROM pedido AS p
JOIN item_pedido AS i ON i.pedido_id = p.id
WHERE p.status = 'pago'
GROUP BY p.cliente_id
HAVING SUM(i.quantidade * i.preco_unitario) >= 30;
```
Se cada pedido tivesse p.total repetido para cada item, somar p.total depois do JOIN contaria o pedido uma vez por item.

