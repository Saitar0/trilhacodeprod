---
arquivo_id: "f9-40-1-04-dead-letter-recuperacao-01-teoria"
parent_key: "40.1"
tipo_arquivo: "theory"
assunto: "04_dead_letter_recuperacao"
ordem: 4
itens_origem: ["### Microtópico 4 — Projetar dead-letter e recuperação de mensagens"]
---


### Microtópico 4 — Projetar dead-letter e recuperação de mensagens

Uma mensagem pode ir para uma **dead-letter exchange (DLX)** quando é rejeitada sem requeue, expira por TTL, excede limites configurados ou encontra outra condição definida pela política/versão. A DLX ainda precisa rotear a mensagem para uma fila ou destino configurado; criar a exchange sem binding/destino não resolve a recuperação.

A configuração padrão de dead-lettering pode republicar sem publisher confirms internos e, em certos modos, perder uma mensagem se o destino não a aceitar. RabbitMQ oferece **at-least-once dead-lettering** para quorum queues com configuração explícita; não é uma garantia automática para toda queue. Essa opção exige políticas apropriadas, consome mais recursos e ainda pode produzir duplicatas no destino durante retries. Verifique versão, tipo de fila, overflow e documentação antes de depender dela.

DLQ é uma fila de triagem, não um cesto de descarte nem uma política automática de recuperação. Defina quem acompanha a fila, alertas para profundidade/idade, classificação do erro, procedimento de correção e como reprocessar com segurança. Preserve causa/headers úteis sem incluir dados sensíveis. Reprocessamento deve manter idempotência, pois a mesma mensagem pode aparecer novamente e uma DLX pode receber duplicatas dependendo da estratégia.

