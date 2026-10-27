---
arquivo_id: "f7-33-1-01-resumo-md"
parent_key: "33.1"
tipo_arquivo: "resumo"
ordem: 0
itens_origem: ["Resumo"]
---

## Resumo
- Produtor, broker e consumidor desacoplam a produção do processamento e introduzem consistência eventual.
- Fila, tópico e suas garantias variam por produto; escolha e documente a semântica.
- Ack de consumo e confirmação de publicação cobrem lados diferentes; falhas podem gerar reentrega.
- Retry limitado atende falhas transitórias; poison messages vão para uma DLQ operada e investigada.
- Idempotência protege efeitos de duplicatas; outbox fecha a escrita dupla local, mas também pode publicar duplicatas.
- Ordenação, concorrência, backlog e capacidade têm de fazer parte do desenho.

