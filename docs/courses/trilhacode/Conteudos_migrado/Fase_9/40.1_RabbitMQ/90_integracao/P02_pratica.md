---
arquivo_id: "f9-40-1-90-integracao-p02-pratica"
parent_key: "40.1"
tipo_arquivo: "practice"
assuntos: ["01_exchange_binding_filas_consumers", "02_confirmacoes_ack_idempotencia", "03_prefetch_trabalho_em_voo"]
ordem: 2
itens_origem: ["P02"]
---


### Atividade 2 — Exercitar publicação, consumo, ack e idempotência
Com broker local descartável, publique uma mensagem de pedido com identificador estável e publisher confirms. Faça o consumer com ack manual e limite de prefetch. Simule: (a) falha antes de gravar; (b) gravação concluída seguida de queda antes do ack; (c) redelivery; (d) publicação sem rota. Use uma store de teste ou efeito simulado e prove que repetir a mensagem não duplica o pedido.

**Entrega:** sequência de eventos com publisher confirm/return e consumer ack, saída dos testes e configuração/justificativa do prefetch.

**Critérios de aceite:** diferencia confirmação de publicação e de consumo; confirma após efeito durável; caso (b) demonstra possível redelivery sem duplicar efeito; caso (d) é detectado; prefetch limita mensagens pendentes.

