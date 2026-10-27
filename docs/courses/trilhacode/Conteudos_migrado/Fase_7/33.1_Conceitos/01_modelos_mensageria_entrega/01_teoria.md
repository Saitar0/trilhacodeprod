---
arquivo_id: "f7-33-1-01-modelos-mensageria-entrega-01-teoria-md"
parent_key: "33.1"
tipo_arquivo: "theory"
assunto: "01_modelos_mensageria_entrega"
ordem: 1
itens_origem: ["### Microtópico 1 — Produtor, broker, fila e tópico", "### Microtópico 2 — Entrega, confirmação e redelivery"]
---

### Microtópico 1 — Produtor, broker, fila e tópico

O **produtor** cria e publica uma mensagem ou evento; o **broker** recebe e encaminha/guarda o trabalho; o **consumidor** lê e executa uma tarefa. Esse caminho desacopla o momento de produção do momento de processamento: o produtor pode responder antes que todo o trabalho termine, enquanto o consumidor escala e recupera de forma independente. O custo inclui atraso, consistência eventual, operação adicional e necessidade de acompanhar trabalho pendente.

Uma **fila** costuma distribuir cada mensagem a um consumidor do grupo para que o trabalho seja feito uma vez no fluxo. Um **tópico** costuma publicar um evento para vários assinantes (fan-out), cada um com sua própria subscrição/fluxo de consumo. Os nomes e as garantias variam entre produtos. No RabbitMQ, por exemplo, exchanges roteiam mensagens para filas; uma exchange de tópico usa padrões de routing key. Não deduza a semântica apenas da palavra “tópico”.

Uma mensagem representa trabalho ou um fato que outro componente precisa conhecer. Diferencie comando (“gere o relatório”) de evento (“relatório foi gerado”). Defina identificador estável, tipo/versão, dados mínimos, instante e chave de negócio/correlação conforme necessidade. Evite colocar segredos ou dados pessoais sem uma necessidade e política de retenção. Mensagem durável, fila durável e confirmação de publicação são controles distintos; nenhum sozinho prova que o efeito de negócio foi concluído.

### Microtópico 2 — Entrega, confirmação e redelivery

Brokers oferecem semânticas diferentes conforme produto, configuração e protocolo. “Pelo menos uma vez” permite reentrega e duplicata; “no máximo uma vez” pode perder trabalho; recursos que anunciam processamento exatamente uma vez têm escopo e condições próprios. Não transforme uma garantia limitada do broker em promessa global de que um efeito externo — como cobrar cartão ou enviar e-mail — ocorrerá uma única vez.

No consumo, um **ack** indica ao broker que a entrega terminou segundo o protocolo; só confirme depois de persistir/realizar o efeito ou de transferir responsabilidade com segurança. Se o processo cair depois do efeito e antes do ack, o broker pode entregar de novo. Se confirmar antes do efeito e cair, o trabalho pode desaparecer. No RabbitMQ, confirmações do consumidor e publisher confirms são mecanismos independentes: publisher confirm trata a aceitação da publicação pelo broker; ack do consumidor trata o processamento da entrega. Um não prova o outro.

Em serviços como SQS, a mensagem pode ficar temporariamente invisível durante o processamento; se não for removida/confirmada antes da janela, pode reaparecer. Ajuste o limite ao tempo de processamento e ao modelo do serviço; nem janela de visibilidade nem ack substituem idempotência. Considere mensagens em trânsito quando dimensionar timeout e recuperação.

