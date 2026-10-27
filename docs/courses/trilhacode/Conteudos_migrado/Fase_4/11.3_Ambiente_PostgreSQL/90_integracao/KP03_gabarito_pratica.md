---
arquivo_id: "f4-11-3-90-integracao-kp03-gabarito-pratica"
parent_key: "11.3"
tipo_arquivo: "answer_key_pratica"
assuntos: ["03_ddl_dml_com_cuidado", "04_confirmacao_reversao_dml"]
ordem: 3
itens_origem: ["P3"]
---

**Solução de referência:**
```sql
BEGIN;
UPDATE pedido
SET status = 'pago'
WHERE id = 1
RETURNING id, cliente_id, status, total;
-- Inspecione o resultado e escolha uma opção:
ROLLBACK;
-- Para persistir uma alteração validada, use COMMIT no lugar de ROLLBACK.
```
O SELECT anterior deve mostrar somente o pedido id 1. Sem WHERE, todas as linhas seriam alteradas. Não execute COMMIT e ROLLBACK na mesma tentativa esperando que ambos tenham efeito: escolha um desfecho por transação.

