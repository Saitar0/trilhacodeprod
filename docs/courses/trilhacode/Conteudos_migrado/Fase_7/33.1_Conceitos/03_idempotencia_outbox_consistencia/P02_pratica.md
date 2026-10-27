---
arquivo_id: "f7-33-1-03-idempotencia-outbox-consistencia-p02-pratica-md"
parent_key: "33.1"
tipo_arquivo: "practice"
assunto: "03_idempotencia_outbox_consistencia"
ordem: 2
itens_origem: ["P02"]
---

### Atividade 2 — Torne o consumidor idempotente

**Desafio:** implemente ou modele um worker que receba duas vezes o mesmo evento sem duplicar o efeito de negócio.

**Passos:**
1. Defina um `event_id` estável e qual efeito precisa acontecer uma única vez logicamente.
2. Desenhe ou implemente o registro de evento processado junto do efeito numa transação/restrição adequada.
3. Inclua dois workers concorrentes tentando processar o mesmo id; determine como a implementação impede a corrida.
4. Simule queda após o commit e antes do ack, e depois repita a entrega.
5. Se o efeito ocorrer num serviço externo, especifique a chave de idempotência ou estratégia de reconciliação; não alegue atomicidade que não existe.

**Evidências:** código/pseudocódigo/diagrama de transação; teste ou tabela de repetição e concorrência; resultado do efeito antes/depois da redelivery.

**Verificação:** duas entregas com o mesmo id não duplicam o efeito; ids distintos continuam gerando operações distintas; falha após commit pode ser recuperada pela redelivery sem perda.

**Aceite:** deduplicação e efeito têm atomicidade ou mecanismo equivalente; cenário concorrente está coberto; limites externos são explícitos.

