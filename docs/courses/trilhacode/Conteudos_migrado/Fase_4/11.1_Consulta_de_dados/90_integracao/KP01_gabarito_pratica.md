---
arquivo_id: "f4-11-1-90-integracao-kp01-gabarito-pratica"
parent_key: "11.1"
tipo_arquivo: "answer_key_pratica"
assuntos: ["01_projecao_alias", "02_filtros_logica_booleana"]
ordem: 1
itens_origem: ["P1"]
---

**Solução de referência:**
```sql
SELECT id, status, total AS valor_pedido, criado_em
FROM pedido
WHERE status = 'pago'
  AND total >= 100;
```
As colunas foram limitadas ao relatório e o alias melhora o rótulo de saída. Se total puder ser NULL, a comparação não seleciona essa linha; defina se isso é aceitável para a regra.

