---
arquivo_id: "f7-33-1-90-integracao-p01-pratica-md"
parent_key: "33.1"
tipo_arquivo: "practice"
assuntos: ["01_modelos_mensageria_entrega", "02_retry_backoff_dlq", "03_idempotencia_outbox_consistencia"]
ordem: 1
itens_origem: ["P01"]
---

### Atividade 1 — Desenhe o ciclo da mensagem e as falhas

**Desafio:** modele um pedido que dispara processamento assíncrono e descreva o que acontece nos pontos de falha.

**Passos:**
1. Desenhe produtor/API → persistência → broker → worker → efeito de negócio → confirmação; identifique onde ficam ack de publicação e ack de consumo, se usados.
2. Defina se a mensagem é comando ou evento, payload mínimo, id, versão e chave de correlação.
3. Simule no diagrama uma falha antes da publicação, depois da publicação e antes/depois do efeito, mas antes do ack.
4. Para cada falha, indique se pode haver perda, duplicata, redelivery ou atraso e qual componente recupera.
5. Descreva o estado que o cliente observa enquanto o worker ainda processa (por exemplo, “pendente” seguido de consulta ou notificação).

**Evidências:** diagrama de sequência; contrato da mensagem; tabela ponto de falha → consequência → recuperação; estado percebido pelo cliente.

**Verificação:** confirme que publicação confirmada não foi confundida com processamento concluído e que queda após efeito e antes do ack pode gerar repetição.

**Aceite:** todos os papéis e confirmações estão identificados; pelo menos três pontos de falha têm consequência e recuperação coerentes; consistência eventual é explicada ao consumidor da API.

