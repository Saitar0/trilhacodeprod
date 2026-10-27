---
arquivo_id: "f9-41-1-90-integracao-p01-pratica"
parent_key: "41.1"
tipo_arquivo: "practice"
assuntos: ["01_fronteiras_orcamento_latencia", "02_timeout_retry_circuit_breaker"]
ordem: 1
itens_origem: ["P01"]
---


### Atividade 1 — Escolha síncrono ou assíncrono
**Contexto:** um checkout precisa (A) validar endereço para mostrar erro imediatamente, (B) enviar e-mail de confirmação e (C) reservar estoque e autorizar pagamento. O objetivo da API é responder em até 2 segundos.

**Instruções:** desenhe um fluxo que identifique quais operações precisam de resposta síncrona e quais podem continuar em segundo plano. Defina resposta da API, estados do pedido, deadline, timeout por chamada, comportamento de indisponibilidade e como o cliente consulta o progresso. Compare com um desenho em que tudo é síncrono.

**Entrega:** diagrama de sequência simples e tabela “operação, modo, timeout/deadline, falha visível, recuperação”. Inclua uma justificativa de até 200 palavras.

**Dica gradual:** separe validação necessária para aceitar a solicitação de efeitos que podem terminar depois; depois distribua o orçamento de 2 s entre as chamadas que restarem.

