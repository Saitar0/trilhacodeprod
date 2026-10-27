---
arquivo_id: "f4-11-1-90-integracao-kp03-gabarito-pratica"
parent_key: "11.1"
tipo_arquivo: "answer_key_pratica"
assuntos: ["03_null_logica_trivalente", "04_ordenacao_limite_previsibilidade"]
ordem: 3
itens_origem: ["P3"]
---

**Solução de referência:**
```sql
SELECT id, criado_em, total
FROM pedido
WHERE total IS NOT NULL
ORDER BY total DESC, id DESC
LIMIT 10;
```
A consulta exclui valores desconhecidos, ordena maior total primeiro e resolve empates por id decrescente. Sem ORDER BY, não há garantia de que as dez linhas escolhidas sejam as de maior total.

