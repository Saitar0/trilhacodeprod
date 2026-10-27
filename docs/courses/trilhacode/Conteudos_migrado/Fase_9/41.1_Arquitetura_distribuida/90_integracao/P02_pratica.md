---
arquivo_id: "f9-41-1-90-integracao-p02-pratica"
parent_key: "41.1"
tipo_arquivo: "practice"
assuntos: ["01_fronteiras_orcamento_latencia", "02_timeout_retry_circuit_breaker"]
ordem: 2
itens_origem: ["P02"]
---


### Atividade 2 — Desenhe a política de resiliência
**Contexto:** uma API tem deadline de 1,5 s. Ela chama inventário (orçamento de 500 ms) e recomendação (orçamento de 300 ms); reserva os 700 ms restantes para processamento e resposta. Inventário falha temporariamente; recomendação pode ser omitida sem comprometer a compra.

**Instruções:** para cada dependência, defina timeout, se retry é aceitável, número máximo de tentativas e backoff dentro do orçamento; diga se um breaker/bulkhead é útil; descreva o fallback aceitável. Explique o que fazer com erro permanente e como evitar retries simultâneos em várias camadas.

**Entrega:** tabela de política, pseudo fluxo para uma chamada e lista de três métricas/alertas. As tentativas e esperas precisam caber nos orçamentos informados.

**Dica gradual:** calcule o tempo total como soma de tentativas, esperas e processamento. Para recomendação, considere retornar sem recomendações; para inventário, não invente disponibilidade.

