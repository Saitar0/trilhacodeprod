---
arquivo_id: "f4-12-3-03-pagamentos-idempotencia-01-teoria"
parent_key: "12.3"
tipo_arquivo: "theory"
assunto: "03_pagamentos_idempotencia"
ordem: 3
itens_origem: ["4. Separe ciclo do pagamento, estado do pedido e integração externa"]
---

### 4. Separe ciclo do pagamento, estado do pedido e integração externa
Pedido e pagamento são conceitos relacionados, mas não são o mesmo registro. Um pedido pode passar por criado, aguardando pagamento, confirmado, cancelado ou reembolsado. Uma tentativa pode ficar pendente, ser recusada, autorizada, capturada ou expirar conforme o provedor. Defina transições válidas e qual evento permite marcar o pedido como pago.

A chamada ao provedor de pagamento ocorre fora da transação local do PostgreSQL. Não mantenha uma transação e locks abertos enquanto espera por uma API externa. Registre a tentativa e a chave de idempotência, envie a solicitação com o recurso do provedor, depois grave o resultado numa nova transação. Se a conexão cair após o provedor processar a solicitação, consulte/reconcilie o estado antes de criar outra cobrança. Uma fila/outbox pode ser necessária para entregas confiáveis em sistemas maiores.

**Erro comum:** supor que ROLLBACK no banco desfaz uma cobrança que já ocorreu no provedor externo.

