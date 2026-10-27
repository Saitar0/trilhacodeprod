---
arquivo_id: "f9-41-1-01-resumo"
parent_key: "41.1"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---


## Resumo
- Timeout limita espera, mas o efeito remoto pode ter acontecido; modele a operação com deadline total.
- Retry é finito, seletivo e seguro para operações idempotentes; backoff e jitter reduzem tempestades de chamadas.
- Circuit breaker interrompe chamadas a dependência degradada; bulkhead limita propagação de saturação.
- Saga coordena transações locais e compensações explícitas; compensação pode falhar e requer estado/reconciliação.
- Outbox torna atômicos o dado local e a intenção de publicar, mas o relay pode duplicar; consumidores devem ser idempotentes.

