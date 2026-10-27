---
arquivo_id: "f9-40-1-02-confirmacoes-ack-idempotencia-01-teoria"
parent_key: "40.1"
tipo_arquivo: "theory"
assunto: "02_confirmacoes_ack_idempotencia"
ordem: 2
itens_origem: ["### Microtópico 2 — Separar confirmação da publicação e confirmação do consumo"]
---


### Microtópico 2 — Separar confirmação da publicação e confirmação do consumo

**Publisher confirms** informam ao publisher que o broker aceitou a publicação conforme a semântica do broker e da fila. Não significam que um consumer recebeu, processou ou confirmou a mensagem. Retorno de mensagem não roteável e publisher confirm também são sinais diferentes: a aplicação deve correlacioná-los com a publicação correta.

**Consumer acknowledgements** fluem no sentido oposto. Com ack manual, o consumer confirma uma entrega depois de concluir o efeito durável. Se confirmar antes de gravar o pedido, uma falha pode apagar a mensagem da fila sem concluir a operação. Se gravar e cair antes do ack, a mensagem pode ser entregue novamente e o efeito pode ser repetido. Por isso, o consumer precisa de idempotência: uma chave estável de negócio ou uma tabela de deduplicação transacional deve impedir que a mesma operação produza efeito duplicado.

`ack` confirma a entrega; `nack`/reject recusa. Requeue pode devolver a mensagem para nova tentativa, mas requeue imediato para erro permanente pode formar um ciclo rápido entre fila e consumer. Diferencie erro transitório de erro permanente. Use número limitado de tentativas e atraso/backoff adequado; ao exceder a política, encaminhe para triagem em vez de tentar para sempre.

Para o publisher, combine fila durável, mensagem persistente quando apropriado, confirmações e tratamento de retornos de acordo com a falha que quer suportar. Confirms reduzem a incerteza sobre a publicação, mas não criam uma transação atômica entre banco de dados da aplicação e RabbitMQ. Se gravar no banco e publicar forem uma única obrigação de negócio, avalie padrões como outbox nas fases de arquitetura distribuída.

