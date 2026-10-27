---
arquivo_id: "f9-40-3-03-ordem-escala-replay-01-teoria"
parent_key: "40.3"
tipo_arquivo: "theory"
assunto: "03_ordem_escala_replay"
ordem: 3
itens_origem: ["### 3. Ordem, escala e replay"]
---


### 3. Ordem, escala e replay
- **Kafka:** a ordem é garantida dentro de uma partição. Usar uma chave consistente direciona eventos relacionados à mesma partição; isso limita paralelismo daquela chave. Consumidores do mesmo grupo dividem partições, e grupos independentes podem ler a mesma retenção com offsets próprios.
- **RabbitMQ:** filas e consumidores distribuem trabalho; concorrência, requeue e redelivery podem alterar a ordem observada. Não assuma ordenação global quando houver múltiplos consumidores ou falhas. O padrão usual não equivale ao replay de um log por offset independente de cada grupo.
- **SQS:** Standard prioriza escala e pode entregar fora de ordem e mais de uma vez. FIFO preserva sequência dentro de um `MessageGroupId`; mensagens daquele grupo podem bloquear as seguintes até serem apagadas ou o visibility timeout expirar. Retenção tem prazo configurado e não é um histórico indefinido.
- **Pub/Sub:** ordenação requer habilitação e chave de ordenação; mensagens relacionadas devem ser publicadas na mesma região conforme a documentação. Redelivery pode repercutir em mensagens seguintes da chave. Retenção/replay dependem das propriedades da assinatura e do tópico.

Pergunta de checagem: é necessário ordenar todos os eventos do sistema ou apenas os eventos de cada pedido/cliente? Ordenação ampla pode reduzir paralelismo; prefira a menor chave de ordenação que satisfaça a regra de negócio.

