---
arquivo_id: "f9-46-3-c03-aceite-falhas-retry-dlq-e-idempotencia"
parent_key: "46.3"
tipo_arquivo: "checklist"
ordem: 3
itens_origem: ["M03"]
titulo_marco: "Entrega 3 — Falhas, retry, DLQ e idempotência"
---


**Critérios de aceite:** redelivery não repete o efeito; falha transitória tem tentativas limitadas; falha permanente chega à DLQ; a mensagem e causa podem ser diagnosticadas; redrive é reprodutível e auditável.
