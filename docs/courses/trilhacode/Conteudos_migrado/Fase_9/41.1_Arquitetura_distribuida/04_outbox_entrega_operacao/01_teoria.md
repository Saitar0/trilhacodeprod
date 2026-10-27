---
arquivo_id: "f9-41-1-04-outbox-entrega-operacao-01-teoria"
parent_key: "41.1"
tipo_arquivo: "theory"
assunto: "04_outbox_entrega_operacao"
ordem: 4
itens_origem: ["### 4. Outbox, entrega e operação observável"]
---


### 4. Outbox, entrega e operação observável
O **dual write** é o risco de gravar no banco e publicar em um broker como ações independentes: uma pode funcionar e a outra falhar. O padrão **transactional outbox** grava a alteração de negócio e uma linha de evento na mesma transação local. Um relay publica eventos pendentes depois.

O relay pode cair após publicar, antes de marcar o evento como enviado; portanto, pode publicar de novo. A outbox evita perder a intenção de publicar junto com a transação local, mas não oferece entrega global exatamente uma vez. Consumidores precisam deduplicar com ID do evento e proteger o efeito de negócio. Mantenha a transação do consumidor e o registro de deduplicação atômicos sempre que possível.

A operação precisa expor:
- idade e quantidade de eventos pendentes na outbox;
- falhas e latência do relay, tentativas e último sucesso;
- tamanho/idade de filas e DLQ, redrives e causa da falha;
- duração da saga por estado, compensações pendentes e processos sem progresso;
- correlação entre requisição, pedido, evento e chamada remota, sem registrar segredos/dados sensíveis.

Defina políticas de retenção, replay e descarte, e um procedimento de redrive que valide a causa, repita com segurança e registre o resultado. Faça teste de falha interrompendo o processo entre gravação, publicação, confirmação e atualização do estado.

**Checagem:** qual falha a outbox resolve e qual ainda exige idempotência? Resolve o dual write entre alteração local e intenção de publicar; repetição da publicação ainda exige deduplicação no consumidor.

