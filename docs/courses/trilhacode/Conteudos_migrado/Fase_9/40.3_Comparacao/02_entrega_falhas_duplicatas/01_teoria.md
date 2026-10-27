---
arquivo_id: "f9-40-3-02-entrega-falhas-duplicatas-01-teoria"
parent_key: "40.3"
tipo_arquivo: "theory"
assunto: "02_entrega_falhas_duplicatas"
ordem: 2
itens_origem: ["### 2. Entrega, falhas e duplicatas"]
---


### 2. Entrega, falhas e duplicatas
- **RabbitMQ:** confirmações do produtor e ack manual do consumidor cobrem partes diferentes do fluxo. Se o consumidor processa o efeito e cai antes do ack, a mensagem pode ser redeliverada. Retry, dead-letter exchange e idempotência precisam fazer parte do desenho.
- **Kafka:** o consumidor confirma posição por offset. O momento de confirmar em relação ao efeito no banco pode produzir reprocessamento ou perda lógica; transações e integração com sistemas externos têm limites próprios. Projetar idempotência e estratégia de commit é essencial.
- **SQS:** a mensagem fica temporariamente invisível após o recebimento; se não for apagada antes do fim do visibility timeout, pode voltar a ser entregue. Standard trabalha com entrega pelo menos uma vez. FIFO oferece ordenação por grupo e deduplicação com janela/condições específicas, sem tornar efeitos externos automaticamente exatamente uma vez.
- **Pub/Sub:** mensagem sem ack pode ser reenviada após o ack deadline; prazo e política de retry afetam o fluxo. Existe entrega exactly-once para assinaturas pull dentro de uma região, com requisitos e limites documentados; isso não impede o produtor de publicar eventos de negócio duplicados.

Em todos os casos, “recebido”, “processado”, “confirmado pelo broker” e “efeito persistido no sistema de destino” são estados diferentes. A proteção prática costuma combinar chave idempotente, registro durável do efeito, política de retry limitada, DLQ e procedimento de redrive.

Pergunta de checagem: se o efeito no banco foi confirmado, mas o ack se perdeu, qual deve ser o comportamento seguro na próxima tentativa?

