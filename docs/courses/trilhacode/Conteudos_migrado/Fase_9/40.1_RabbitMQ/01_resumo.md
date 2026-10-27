---
arquivo_id: "f9-40-1-01-resumo"
parent_key: "40.1"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---


## Resumo
- Publisher publica numa exchange; bindings levam a filas conforme a routing key e o tipo de exchange. A exchange padrão tem vínculo implícito por nome da fila.
- Publisher confirm valida a etapa de publicação; consumer ack informa conclusão da entrega. Nenhum substitui o outro.
- Confirmar antes do efeito durável pode perder trabalho; confirmar depois do efeito pode gerar redelivery se houver queda. Idempotência protege contra duplicação.
- Prefetch limita mensagens sem ack e troca memória/trabalho em voo por throughput; calibre com medições.
- Retry precisa de limite e estratégia para evitar loops; DLQ exige destino, triagem e reprocessamento seguro.
- Durabilidade e at-least-once dead-lettering dependem de queue type, configuração e versão; não presuma a mesma garantia para todas as filas.

