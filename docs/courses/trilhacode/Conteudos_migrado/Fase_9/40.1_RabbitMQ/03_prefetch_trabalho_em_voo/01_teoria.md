---
arquivo_id: "f9-40-1-03-prefetch-trabalho-em-voo-01-teoria"
parent_key: "40.1"
tipo_arquivo: "theory"
assunto: "03_prefetch_trabalho_em_voo"
ordem: 3
itens_origem: ["### Microtópico 3 — Controlar trabalho em voo com ack manual e prefetch"]
---


### Microtópico 3 — Controlar trabalho em voo com ack manual e prefetch

**Prefetch** limita quantas entregas podem permanecer sem confirmação no escopo configurado. Quando o limite é atingido, o broker pausa novas entregas até receber acks. Um limite baixo reduz mensagens em voo e memória ocupada e pode distribuir trabalho com mais equilíbrio. Um limite maior pode elevar throughput quando o consumer processa rápido, mas aumenta o trabalho em voo e o impacto de queda/reconexão.

Não existe valor universal. Compare consumidores, volume/tamanho de mensagem, duração e variabilidade do processamento, memória disponível e comportamento de redelivery. Prefetch `0` costuma significar sem limite no modelo AMQP 0-9-1, e pode resultar em buffer excessivo se o consumer acumular mensagens. O escopo exato da configuração pode depender de canal, consumer e biblioteca cliente; consulte a versão usada.

Consumer ack manual e publisher confirms protegem trechos diferentes do fluxo. Confirme apenas depois do efeito que deseja proteger; limite o número de mensagens sem ack; e faça o processamento idempotente. Monitore fila pronta, mensagens não confirmadas, consumers ativos, redeliveries e idade da mensagem mais antiga para detectar backlog e consumer travado.

