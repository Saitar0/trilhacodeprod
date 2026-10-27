---
arquivo_id: "f7-33-1-03-idempotencia-outbox-consistencia-k05-gabarito-quiz-md"
parent_key: "33.1"
tipo_arquivo: "answer_key"
assunto: "03_idempotencia_outbox_consistencia"
ordem: 5
itens_origem: ["Q05"]
---

**Resposta esperada:** falha entre gravação e publicação pode deixar pedido sem evento; gravar pedido e registro de outbox na mesma transação local permite publicação posterior. O publicador pode duplicar, então consumidor idempotente continua necessário.

