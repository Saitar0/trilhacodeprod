---
arquivo_id: "f7-33-1-03-idempotencia-outbox-consistencia-01-teoria-md"
parent_key: "33.1"
tipo_arquivo: "theory"
assunto: "03_idempotencia_outbox_consistencia"
ordem: 3
itens_origem: ["### Microtópico 4 — Idempotência, outbox e consistência"]
---

### Microtópico 4 — Idempotência, outbox e consistência

Uma operação é **idempotente** quando repetir a mesma solicitação lógica preserva o mesmo efeito observável. Use identificador de evento ou chave de negócio para reconhecer duplicatas e garanta atomicidade entre “registrar que já processei” e o efeito no banco. Uma checagem em cache separada da gravação pode correr em paralelo: dois workers leem “não processado” ao mesmo tempo e ambos executam. Uma restrição única ou transação que agrupa registro e efeito pode fechar essa corrida quando o efeito está no mesmo banco.

Se a operação de consumo inclui uma API externa, não é possível presumir uma única transação local que cubra banco, broker e serviço externo. Use chave de idempotência suportada pelo serviço remoto, uma máquina de estados/reconciliação ou fluxo compensatório apropriado. Registre limites e janela de retenção da deduplicação.

O produtor também tem uma falha de escrita dupla: grava no banco, mas cai antes de publicar; ou publica e a gravação do negócio falha. O padrão **transactional outbox** grava a mudança de negócio e o evento pendente na mesma transação local; um publicador separado envia depois. Ainda pode haver publicação duplicada, portanto o consumidor continua idempotente. A outbox resolve a atomicidade entre gravação local e intenção de publicar, não torna toda a cadeia distribuída uma única transação.

Ordenação e concorrência também precisam de escopo. Se eventos de uma mesma entidade dependem de ordem, use chave/partição/grupo apropriado e não processe em paralelo sem preservar a sequência relevante. Considere backlog, taxa de chegada/processamento, tamanho do payload, reentrega, duração de processamento e profundidade da DLQ como sinais operacionais. A escolha depende do caso; mais consumidores não resolvem uma fila de eventos inválidos nem um produtor permanentemente mais rápido que a capacidade de processamento.

