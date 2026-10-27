---
arquivo_id: "f9-41-1-90-integracao-p03-pratica"
parent_key: "41.1"
tipo_arquivo: "practice"
assuntos: ["03_consistencia_saga_compensacao", "04_outbox_entrega_operacao"]
ordem: 3
itens_origem: ["P03"]
---


### Atividade 3 — Saga e outbox sob falha
**Contexto:** pedido `P-42` é gravado no serviço de pedidos. Uma etapa reserva estoque, outra autoriza pagamento e um evento `PedidoConfirmado` informa o serviço de notificações. O broker redelivera mensagens e compensar pagamento pode falhar temporariamente.

**Instruções:** desenhe a sequência nominal e três falhas: (1) pedido gravado, processo cai antes da publicação; (2) relay publica, cai antes de marcar enviado; (3) pagamento autorizado, reserva/etapa posterior falha e compensação retorna erro. Escolha orquestração ou coreografia e justifique. Defina estados, chaves idempotentes, registros da outbox/inbox, tentativas, DLQ/reconciliação e mensagem apresentada ao usuário.

**Entrega:** diagrama de estados da saga, esquema mínimo de campos do evento/outbox e procedimento para detectar e recuperar uma compensação pendente. O procedimento não pode apagar evidência nem repetir cobrança.

**Dica gradual:** localize a transação de cada serviço; identifique qual ação pode ter acontecido apesar do timeout; só então desenhe a compensação e a deduplicação.

