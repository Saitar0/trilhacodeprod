---
arquivo_id: "f9-40-1-01-exchange-binding-filas-consumers-01-teoria"
parent_key: "40.1"
tipo_arquivo: "theory"
assunto: "01_exchange_binding_filas_consumers"
ordem: 1
itens_origem: ["### Microtópico 1 — Modelar exchange, binding, fila e consumer"]
---


### Microtópico 1 — Modelar exchange, binding, fila e consumer

No fluxo AMQP 0-9-1, um **publisher** publica numa **exchange** com uma routing key. A exchange aplica seu tipo de roteamento aos **bindings** que ligam exchange e filas. A **queue** mantém mensagens para consumo; consumers ligados à mesma fila competem, de modo que uma entrega é direcionada a um consumer disponível. Duas filas vinculadas podem receber cópias independentes da mesma publicação.

Há uma nuance importante: a exchange padrão (`""`) é uma direct exchange pré-declarada e cada fila é vinculada a ela, por padrão, usando o nome da fila como routing key. Assim, uma aplicação pode publicar na exchange padrão com o nome da fila como chave; isso é uma rota especial que simplifica endereçamento, não elimina o modelo de exchange/binding.

- **Direct:** compara routing key exatamente com a binding key.
- **Topic:** compara segmentos separados por ponto; `*` corresponde a um segmento e `#` corresponde a zero ou mais segmentos.
- **Fanout:** envia cópia a todas as filas ligadas e ignora routing key.
- **Headers:** roteia por cabeçalhos da mensagem segundo os argumentos do binding.

Escolha a topologia pela pergunta de negócio. Por exemplo, `orders.created` pode ser roteada por topic para uma fila de faturamento e outra de notificação; cada fila processa sua própria cópia. Se a mensagem não casar com nenhum binding, ela pode ficar sem destino. Publisher que precisa detectar esse caso deve usar e tratar o mecanismo de retorno (`mandatory`/Basic.Return), ou configurar uma alternate exchange, conforme o desenho.

Durabilidade de exchange, fila, binding e mensagem são aspectos distintos. Uma fila durable não torna uma publicação automaticamente persistente; uma mensagem persistente também não prova que chegou ao destino. Considere tipo de fila, persistência, publisher confirms e o modo de falha que a arquitetura precisa tolerar.

