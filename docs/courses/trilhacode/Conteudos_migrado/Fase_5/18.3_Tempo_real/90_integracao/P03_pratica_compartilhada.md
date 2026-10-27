---
arquivo_id: "f5-18-3-90-integracao-p03-pratica-compartilhada"
parent_key: "18.3"
tipo_arquivo: "practice"
assuntos: ["02_eventos_ordem_e_retomada", "03_seguranca_de_canais", "04_estado_compartilhado_e_concorrencia"]
ordem: 3
itens_origem: ["P3"]
---

### Atividade 3 — Testar queda, repetição e concorrência
Interrompa a conexão de um cliente e reconecte. Para SSE, envie um evento com ID e demonstre como o servidor trata Last-Event-ID enquanto o evento ainda está retido; para WebSocket, implemente política explícita de retry com atraso crescente e variação aleatória. Reenvie uma mensagem já processada e simule uma atualização concorrente. Registre o resultado e as limitações do protótipo.

**Dica:** se o cursor for anterior ao período retido, retorne um sinal claro para buscar o estado atual em HTTP. Não tente reproduzir histórico ilimitado sem uma política de retenção.

