---
arquivo_id: "f8-37-3-02-pubsub-entrega-idempotencia-01-teoria-md"
parent_key: "37.3"
tipo_arquivo: "theory"
assunto: "02_pubsub_entrega_idempotencia"
ordem: 2
itens_origem: ["### Microtópico 2 — Usar Pub/Sub sem presumir entrega única"]
---

### Microtópico 2 — Usar Pub/Sub sem presumir entrega única

O **Pub/Sub** separa quem publica uma mensagem de quem a processa. Publishers publicam em um tópico; uma assinatura (**subscription**) representa uma relação de consumo e entrega mensagens a subscribers. Esse desacoplamento permite que produtores e consumidores evoluam em ritmos diferentes e ajuda a distribuir eventos para consumidores independentes.

O consumidor precisa definir o que significa processar e confirmar uma mensagem. Em sistemas distribuídos, uma falha pode ocorrer entre produzir o efeito de negócio e confirmar o recebimento. Por isso, o processamento deve considerar reentrega e idempotência: repetir a mesma mensagem não deve criar efeitos duplicados indevidos. Ordenação, retenção, política de retry, dead-letter e prazo de confirmação são configurações e garantias a estudar, não consequências automáticas de existir um tópico.

Pub/Sub oferece uma opção de entrega exactly-once com escopo delimitado: exige subscription do tipo pull, opera dentro de uma região e possui requisitos e limites próprios. Mesmo quando esse recurso é habilitado, a aplicação ainda precisa coordenar seu efeito de negócio com a confirmação. A semântica não deve ser resumida como “o sistema inteiro processa cada evento exatamente uma vez”.

AWS SNS, SQS e EventBridge podem participar de arquiteturas que atendem necessidades parecidas, mas seus papéis e combinações não correspondem diretamente a tópico e assinatura do Pub/Sub. Compare o padrão completo — publicação, roteamento, consumo, confirmação, retry e tratamento de falhas — em vez de comparar só nomes.

