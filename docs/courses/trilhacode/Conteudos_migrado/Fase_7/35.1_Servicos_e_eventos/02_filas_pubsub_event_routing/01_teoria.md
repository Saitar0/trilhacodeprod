---
arquivo_id: "f7-35-1-02-filas-pubsub-event-routing-01-teoria-md"
parent_key: "35.1"
tipo_arquivo: "theory"
assunto: "02_filas_pubsub_event_routing"
ordem: 2
itens_origem: ["### Microtópico 2 — Escolha fila, pub/sub ou roteamento de evento"]
---

### Microtópico 2 — Escolha fila, pub/sub ou roteamento de evento

Use **SQS** quando um produtor precisa desacoplar e reter trabalho para consumidores que processam no próprio ritmo. Consumidores leem da fila; mensagens não confirmadas podem reaparecer. SQS Standard favorece escala e pode entregar duplicatas ou fora de ordem; FIFO atende casos em que ordem/deduplicação configuradas são necessárias, dentro de suas garantias e limitações. Verifique tipo de fila, janela de visibilidade, retenção, DLQ e concorrência conforme o contrato. A combinação SQS→Lambda continua sujeita a processamento pelo menos uma vez: função idempotente é necessária.

Use **SNS** quando o produtor publica uma notificação para vários assinantes e quer fan-out (por exemplo, mais de uma fila SQS ou função Lambda). SNS empurra para assinaturas; cada consumidor precisa ter comportamento apropriado para sua entrega. Combinar SNS com uma fila SQS por consumidor permite fan-out com buffer e ritmos independentes, preservando mensagens para processamento posterior dentro da política da fila. A política de acesso precisa permitir a entrega do tópico a cada destino.

Use **EventBridge** quando eventos de domínios/serviços precisam ser roteados por regras e padrões de conteúdo para um ou mais destinos, reduzindo dependência direta entre produtor e consumidor. Um event bus recebe eventos; regras filtram e encaminham. Um evento sem regra correspondente não chega a um destino. Falhas de entrega a target têm retry e DLQ configuráveis conforme serviço, tipo de target e política. Configure métricas, DLQ e alarmes apropriados; não assuma que “usar EventBridge” por si só garante armazenamento indefinido ou reprocessamento.

As opções podem ser compostas. Por exemplo, EventBridge pode filtrar e encaminhar eventos para uma fila SQS, que absorve pico e permite consumo posterior; SNS pode distribuir o mesmo anúncio para filas isoladas por serviço. Compare quem é produtor, quem precisa receber, se há buffer, como selecionar eventos, qual ordenação é necessária e quanto tempo a mensagem precisa permanecer disponível.

