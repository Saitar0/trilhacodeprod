---
arquivo_id: "f8-37-3-90-integracao-p02-pratica-md"
parent_key: "37.3"
tipo_arquivo: "practice"
assuntos: ["01_modelos_de_execucao_cloud_run", "02_pubsub_entrega_idempotencia"]
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Revisão de risco de migração
Considere um consumidor de eventos que grava uma cobrança em banco e só depois confirma a mensagem. Monte uma revisão curta para decidir o que precisa ser validado antes de mover a solução para Pub/Sub e Cloud Run ou para uma configuração equivalente.

Inclua: (a) como evitar cobrança duplicada após reentrega; (b) quando e como confirmar ou rejeitar a mensagem; (c) requisitos de ordenação, retry e dead-letter; (d) identidade e acesso ao banco; (e) observabilidade, quotas, região e custo; (f) uma estratégia de teste sem criar conta ou recursos cloud.

**Entrega:** checklist de riscos com evidência que demonstraria cada item resolvido.

**Critérios de aceite:** os seis aspectos aparecem; distingue garantia de entrega de garantia do efeito de negócio; propõe idempotência ou deduplicação e teste de falha entre gravação e confirmação.

**Feedback esperado:** “ativar exactly-once” isoladamente não resolve a janela entre a gravação no banco e a confirmação; explicite como a aplicação reconhece uma repetição.

