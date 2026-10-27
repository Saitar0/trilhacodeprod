---
arquivo_id: "f7-33-1-02-retry-backoff-dlq-01-teoria-md"
parent_key: "33.1"
tipo_arquivo: "theory"
assunto: "02_retry_backoff_dlq"
ordem: 2
itens_origem: ["### Microtópico 3 — Retry, backoff, poison message e DLQ"]
---

### Microtópico 3 — Retry, backoff, poison message e DLQ

Retry é adequado a falhas **transitórias**, como indisponibilidade breve ou limite de taxa, desde que repetir seja seguro. Uma falha permanente — formato inválido, regra impossível ou incompatibilidade de versão — tende a falhar sempre e não deve repetir sem limite. Defina número máximo/taxa de tentativas, backoff crescente, jitter quando necessário, timeout e classificação de erro. Retry imediato e ilimitado pode criar uma tempestade que piora a indisponibilidade.

Uma mensagem que bloqueia repetidamente o consumo é uma **poison message**. A **dead-letter queue (DLQ)** separa entregas que esgotaram uma política ou foram rejeitadas para diagnóstico e tratamento. DLQ não corrige a mensagem automaticamente: precisa de alerta, retenção, dono, investigação, correção do problema e procedimento controlado de redrive. Antes de reprocessar, confirme se o efeito anterior aconteceu, se a mensagem continua válida, se a versão do consumidor consegue interpretá-la e se duplicatas são seguras. DLQ sem monitoração é só um lugar onde falhas ficam esquecidas.

A configuração concreta é específica do broker. Por exemplo, um limite de recebimentos, redrive policy ou dead-letter exchange pode contar tentativas de forma distinta. Documente o mecanismo escolhido e não suponha que qualquer rejeição significa “uma tentativa” igual em todos os produtos.

