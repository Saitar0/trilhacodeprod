---
arquivo_id: "f9-41-2-90-integracao-p03-pratica"
parent_key: "41.2"
tipo_arquivo: "practice"
assuntos: ["02_custo_prontidao_operacional", "04_extracao_incremental_reversao"]
ordem: 3
itens_origem: ["P03"]
---


### Atividade 3 — Plano de extração gradual e reversão
**Contexto:** após medição, notificações atrasam o processamento do checkout em picos. Regras de notificação são coesas, podem ser acionadas por evento, e a equipe decidiu testar um worker isolado. A aplicação antiga continuará operando durante o piloto.

**Instruções:** planeje a migração em etapas: adaptador/interface, emissão do evento, consumidor novo, roteamento gradual, comparação e retirada da implementação antiga. Especifique fonte da verdade, idempotência, prevenção de escrita dupla, métricas e alarmes, critérios de sucesso e rollback. Inclua o caso em que o worker enviou e-mail mas caiu antes de confirmar o evento.

**Entrega:** plano de rollout com etapas, checklist antes/depois, métricas e um procedimento de rollback que considere mensagens já processadas e dados/eventos persistidos.

**Dica gradual:** marque cada etapa em que o evento pode ser duplicado, atrasado ou perdido; defina chave idempotente e mecanismo de reconciliação antes de aumentar tráfego.

