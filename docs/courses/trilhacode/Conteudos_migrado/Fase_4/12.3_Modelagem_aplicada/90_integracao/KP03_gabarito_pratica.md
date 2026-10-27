---
arquivo_id: "f4-12-3-90-integracao-kp03-gabarito-pratica"
parent_key: "12.3"
tipo_arquivo: "answer_key_pratica"
assuntos: ["02_invariantes_constraints_transacoes", "03_pagamentos_idempotencia", "04_consultas_sem_multiplicacao"]
ordem: 3
itens_origem: ["P3"]
---

**Solução de referência:** inicie uma transação; atualize saldo usando `WHERE disponivel >= 1 RETURNING`; se nenhuma linha for retornada, reverta e informe falta de estoque ou produto ausente; caso retorne, grave item e alterações relacionadas e confirme. Para receita baseada em pedido pago, agregue itens por pedido antes de juntá-los ao pedido:

```sql
WITH total_por_pedido AS (
  SELECT pedido_id, SUM(quantidade * preco_unitario) AS total
  FROM item_pedido
  GROUP BY pedido_id
)
SELECT date_trunc('month', p.criado_em) AS mes, SUM(t.total) AS receita
FROM pedido AS p
JOIN total_por_pedido AS t ON t.pedido_id = p.id
WHERE p.status = 'pago'
GROUP BY date_trunc('month', p.criado_em)
ORDER BY mes;
```

A consulta não junta tentativas de pagamento às linhas de item, então não multiplica as somas por tentativa. Para valor capturado, agregue capturas/reembolsos em sua própria granularidade e política, depois combine com pedidos. Invariantes possíveis: estoque nunca negativo e cada chave do provedor/chave de idempotência é única; verifique por constraints e consultas de auditoria/testes de transação.

